import asyncio
import io
import sys
import types

import pytest

from pybotx.domain.ports.http_client import (
    HttpRequest,
    HttpStatusError,
    HttpTimeoutError,
    HttpTransportError,
)
from pybotx.infrastructure.aiohttp_client import AioHttpClientAdapter, AioHttpResponse


class DummyContent:
    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks

    async def iter_chunked(self, size: int):  # type: ignore[no-untyped-def]
        for chunk in self._chunks:
            yield chunk


class DummyResponse:
    def __init__(
        self,
        *,
        status: int,
        chunks: list[bytes],
        url: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self._chunks = chunks
        self._body = b"".join(chunks)
        self.url = url
        self.closed = False
        self.headers = headers or {}
        self.content = DummyContent(chunks)

    async def read(self) -> bytes:
        return self._body


class DummyResponseContext:
    def __init__(self, response: DummyResponse) -> None:
        self._response = response

    async def __aenter__(self) -> DummyResponse:
        return self._response

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self._response.closed = True


class DummySession:
    def __init__(self, response: DummyResponse | None, error: Exception | None = None) -> None:
        self._response = response
        self._error = error
        self.closed = False
        self.last_args: tuple | None = None
        self.last_kwargs: dict | None = None

    def request(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        self.last_args = args
        self.last_kwargs = kwargs
        if self._error is not None:
            raise self._error
        assert self._response is not None
        return DummyResponseContext(self._response)

    async def close(self) -> None:
        self.closed = True


def _install_aiohttp_stub(
    monkeypatch: pytest.MonkeyPatch,
    *,
    session_factory,
):
    module = types.ModuleType("aiohttp")

    class ClientError(Exception):
        pass

    class ClientTimeout:
        def __init__(self, total: float | None = None) -> None:
            self.total = total

    class FormData:
        def __init__(self) -> None:
            self.fields: list[dict] = []

        def add_field(
            self,
            name: str,
            value: object,
            filename: str | None = None,
            content_type: str | None = None,
        ) -> None:
            self.fields.append(
                {
                    "name": name,
                    "value": value,
                    "filename": filename,
                    "content_type": content_type,
                }
            )

    def ClientSession(*args, **kwargs):  # type: ignore[no-untyped-def]
        return session_factory()

    module.ClientError = ClientError
    module.ClientTimeout = ClientTimeout
    module.ClientSession = ClientSession
    module.FormData = FormData

    monkeypatch.setitem(sys.modules, "aiohttp", module)
    return module


@pytest.mark.asyncio
async def test__aiohttp_client_adapter__request_success(monkeypatch: pytest.MonkeyPatch) -> None:
    response = DummyResponse(status=200, chunks=[b'{"ok": true}'], url="https://test")
    session = DummySession(response)
    _install_aiohttp_stub(monkeypatch, session_factory=lambda: session)

    adapter = AioHttpClientAdapter(timeout=1.0, session=session)
    result = await adapter.send(HttpRequest(method="GET", url="https://test"))

    assert result.status_code == 200
    assert result.content == b'{"ok": true}'
    assert result.json() == {"ok": True}
    assert result.request.method == "GET"
    assert str(result.request.url) == "https://test"
    assert result.is_closed
    assert await result.read() == b'{"ok": true}'
    result.raise_for_status()


@pytest.mark.asyncio
async def test__aiohttp_client_adapter__request_converts_files(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = DummyResponse(status=200, chunks=[b"ok"], url="https://test")
    session = DummySession(response)
    aiohttp_stub = _install_aiohttp_stub(monkeypatch, session_factory=lambda: session)

    adapter = AioHttpClientAdapter(timeout=1.0, session=session)
    file_obj = io.BytesIO(b"payload")
    await adapter.send(
        HttpRequest(
            method="POST",
            url="https://test",
            data={"meta": "1"},
            files={
                "content": ("file.txt", file_obj),
                "image": ("image.png", io.BytesIO(b"img"), "image/png"),
                "odd": ("single",),
                "raw": b"raw",
            },
        )
    )

    form = session.last_kwargs["data"]
    assert isinstance(form, aiohttp_stub.FormData)
    assert form.fields[0]["name"] == "meta"
    assert form.fields[0]["value"] == "1"
    assert form.fields[1]["filename"] == "file.txt"
    assert form.fields[2]["content_type"] == "image/png"
    assert form.fields[3]["value"] == ("single",)
    assert form.fields[4]["value"] == b"raw"

    await adapter.send(
        HttpRequest(
            method="POST",
            url="https://test",
            files={"raw": b"raw"},
        )
    )


@pytest.mark.asyncio
async def test__aiohttp_client_adapter__request_client_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = DummyResponse(status=200, chunks=[b"ok"], url="https://test")
    session = DummySession(response)
    aiohttp_stub = _install_aiohttp_stub(monkeypatch, session_factory=lambda: session)

    session._error = aiohttp_stub.ClientError("boom")
    adapter = AioHttpClientAdapter(timeout=1.0, session=session)

    with pytest.raises(HttpTransportError):
        await adapter.send(HttpRequest(method="GET", url="https://test"))


@pytest.mark.asyncio
async def test__aiohttp_client_adapter__stream_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = DummyResponse(status=200, chunks=[b"", b"a", b"b"], url="https://test")
    session = DummySession(response)
    _install_aiohttp_stub(monkeypatch, session_factory=lambda: session)

    adapter = AioHttpClientAdapter(timeout=1.0, session=session)

    async with adapter.stream(HttpRequest(method="GET", url="https://test")) as result:
        assert not result.is_closed
        collected = b"".join([chunk async for chunk in result.iter_bytes()])

    assert collected == b"ab"
    assert result.is_closed
    collected_after_close = b"".join([chunk async for chunk in result.iter_bytes()])
    assert collected_after_close == b""


@pytest.mark.asyncio
async def test__aiohttp_client_adapter__stream_client_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = DummyResponse(status=200, chunks=[b"ok"], url="https://test")
    session = DummySession(response)
    aiohttp_stub = _install_aiohttp_stub(monkeypatch, session_factory=lambda: session)

    session._error = aiohttp_stub.ClientError("boom")
    adapter = AioHttpClientAdapter(timeout=1.0, session=session)

    with pytest.raises(HttpTransportError):
        async with adapter.stream(HttpRequest(method="GET", url="https://test")):
            pass


@pytest.mark.asyncio
async def test__aiohttp_response__read_reads_body() -> None:
    response = DummyResponse(status=200, chunks=[b"x", b"y"], url="https://test")
    wrapper = AioHttpResponse(
        response=response,
        request=HttpRequest(method="GET", url="https://test"),
    )

    assert await wrapper.read() == b"xy"


@pytest.mark.asyncio
async def test__aiohttp_response__aiter_bytes_closed_uses_body() -> None:
    response = DummyResponse(status=200, chunks=[b"xy"], url="https://test")
    response.closed = True
    wrapper = AioHttpResponse(
        response=response,
        request=HttpRequest(method="GET", url="https://test"),
        body=b"xy",
    )

    collected = b"".join([chunk async for chunk in wrapper.iter_bytes()])
    assert collected == b"xy"


def test__aiohttp_response__raise_for_status() -> None:
    response = DummyResponse(status=500, chunks=[b"err"], url="https://test")
    wrapper = AioHttpResponse(
        response=response,
        request=HttpRequest(method="GET", url="https://test"),
        body=b"err",
    )

    with pytest.raises(HttpStatusError) as exc:
        wrapper.raise_for_status()

    assert exc.value.response.status_code == 500
    assert exc.value.response.content == b"err"


def test__aiohttp_response__headers() -> None:
    response = DummyResponse(
        status=200,
        chunks=[b"ok"],
        url="https://test",
        headers={"x-id": "1"},
    )
    wrapper = AioHttpResponse(
        response=response,
        request=HttpRequest(method="GET", url="https://test"),
        body=b"ok",
    )

    assert wrapper.headers == {"x-id": "1"}


@pytest.mark.asyncio
async def test__aiohttp_client_adapter__request_kwargs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = DummyResponse(status=200, chunks=[b"ok"], url="https://test")
    session = DummySession(response)
    aiohttp_stub = _install_aiohttp_stub(monkeypatch, session_factory=lambda: session)

    adapter = AioHttpClientAdapter(timeout=1.0, session=session)
    await adapter.send(
        HttpRequest(
            method="POST",
            url="https://test",
            headers={"x": "1"},
            params={"q": "2"},
            json={"k": "v"},
            timeout=5.0,
        )
    )

    assert session.last_kwargs["headers"] == {"x": "1"}
    assert session.last_kwargs["params"] == {"q": "2"}
    assert session.last_kwargs["json"] == {"k": "v"}
    assert isinstance(session.last_kwargs["timeout"], aiohttp_stub.ClientTimeout)
    assert session.last_kwargs["timeout"].total == 5.0


@pytest.mark.asyncio
async def test__aiohttp_client_adapter__request_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = DummyResponse(status=200, chunks=[b"ok"], url="https://test")
    session = DummySession(response, error=asyncio.TimeoutError())
    _install_aiohttp_stub(monkeypatch, session_factory=lambda: session)

    adapter = AioHttpClientAdapter(timeout=1.0, session=session)
    with pytest.raises(HttpTimeoutError):
        await adapter.send(HttpRequest(method="GET", url="https://test"))


@pytest.mark.asyncio
async def test__aiohttp_client_adapter__stream_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = DummyResponse(status=200, chunks=[b"ok"], url="https://test")
    session = DummySession(response, error=asyncio.TimeoutError())
    _install_aiohttp_stub(monkeypatch, session_factory=lambda: session)

    adapter = AioHttpClientAdapter(timeout=1.0, session=session)

    with pytest.raises(HttpTimeoutError):
        async with adapter.stream(HttpRequest(method="GET", url="https://test")):
            pass


def test__aiohttp_client_adapter__missing_dependency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delitem(sys.modules, "aiohttp", raising=False)
    real_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # type: ignore[override]
        if name == "aiohttp":
            raise ModuleNotFoundError("No module named 'aiohttp'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(ModuleNotFoundError):
        AioHttpClientAdapter(timeout=1.0, session=DummySession(None))


@pytest.mark.asyncio
async def test__aiohttp_client_adapter__aclose_owns_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = DummyResponse(status=200, chunks=[b"ok"], url="https://test")
    session = DummySession(response)
    _install_aiohttp_stub(monkeypatch, session_factory=lambda: session)

    adapter = AioHttpClientAdapter(timeout=1.0)
    await adapter.aclose()

    assert session.closed


@pytest.mark.asyncio
async def test__aiohttp_client_adapter__aclose_foreign_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = DummyResponse(status=200, chunks=[b"ok"], url="https://test")
    session = DummySession(response)
    _install_aiohttp_stub(monkeypatch, session_factory=lambda: session)

    adapter = AioHttpClientAdapter(timeout=1.0, session=session)
    await adapter.aclose()

    assert not session.closed
