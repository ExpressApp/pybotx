import httpx
import pytest

from pybotx.domain.ports.http_client import (
    HttpRequest,
    HttpStatusError,
    HttpTimeoutError,
    HttpTransportError,
)
from pybotx.infrastructure.httpx_client import HttpxClientAdapter, HttpxResponse


class _TimeoutTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("boom")


class _ErrorTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")


class _OkTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"ok", request=request)


class _DummyAsyncStream(httpx.AsyncByteStream):
    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks

    async def __aiter__(self):
        for chunk in self._chunks:
            yield chunk

    async def aclose(self) -> None:
        return None


class _OkAsyncStreamTransport(httpx.AsyncBaseTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            stream=_DummyAsyncStream([b"hello", b"world"]),
            request=request,
        )


class _DummySyncClient:
    def build_request(  # type: ignore[no-untyped-def]
        self,
        method,
        url,
        headers=None,
        params=None,
        json=None,
        data=None,
        files=None,
        timeout=None,
    ) -> httpx.Request:
        return httpx.Request(method, url, headers=headers, params=params, json=json, data=data, files=files)

    async def send(self, request: httpx.Request, stream: bool = True) -> httpx.Response:
        return httpx.Response(200, stream=httpx.ByteStream(b"ok"), request=request)


@pytest.mark.asyncio
async def test__httpx_response__read_sync_and_headers() -> None:
    request = HttpRequest(method="GET", url="https://example.org")
    response = httpx.Response(200, content=b"payload", request=httpx.Request("GET", request.url))
    wrapper = HttpxResponse(response=response, request=request)

    data = await wrapper.read()

    assert data == b"payload"
    assert wrapper.headers == dict(response.headers)
    assert wrapper.content == b"payload"
    assert wrapper.request is request


@pytest.mark.asyncio
async def test__httpx_response__read_async_stream() -> None:
    request = HttpRequest(method="GET", url="https://example.org")
    response = httpx.Response(
        200,
        stream=_DummyAsyncStream([b"hello", b"world"]),
        request=httpx.Request("GET", request.url),
    )
    wrapper = HttpxResponse(response=response, request=request)

    data = await wrapper.read()

    assert data == b"helloworld"


def test__httpx_response__raise_for_status() -> None:
    request = HttpRequest(method="GET", url="https://example.org")
    response = httpx.Response(400, request=httpx.Request("GET", request.url))
    wrapper = HttpxResponse(response=response, request=request)

    with pytest.raises(HttpStatusError):
        wrapper.raise_for_status()


@pytest.mark.asyncio
async def test__httpx_client_adapter__send_timeout() -> None:
    client = httpx.AsyncClient(transport=_TimeoutTransport())
    adapter = HttpxClientAdapter(client)
    request = HttpRequest(method="GET", url="https://example.org")

    with pytest.raises(HttpTimeoutError):
        await adapter.send(request)

    await client.aclose()


@pytest.mark.asyncio
async def test__httpx_client_adapter__send_transport_error() -> None:
    client = httpx.AsyncClient(transport=_ErrorTransport())
    adapter = HttpxClientAdapter(client)
    request = HttpRequest(method="GET", url="https://example.org")

    with pytest.raises(HttpTransportError):
        await adapter.send(request)

    await client.aclose()


@pytest.mark.asyncio
async def test__httpx_client_adapter__send_success_sync_stream() -> None:
    client = httpx.AsyncClient(transport=_OkTransport())
    adapter = HttpxClientAdapter(client)
    request = HttpRequest(method="GET", url="https://example.org")

    response = await adapter.send(request)

    assert response.content == b"ok"
    await client.aclose()


@pytest.mark.asyncio
async def test__httpx_client_adapter__send_success_async_stream() -> None:
    client = httpx.AsyncClient(transport=_OkAsyncStreamTransport())
    adapter = HttpxClientAdapter(client)
    request = HttpRequest(method="GET", url="https://example.org")

    response = await adapter.send(request)

    assert response.content == b"helloworld"
    await client.aclose()


@pytest.mark.asyncio
async def test__httpx_client_adapter__send_success_sync_stream_via_dummy() -> None:
    client = _DummySyncClient()
    adapter = HttpxClientAdapter(client)  # type: ignore[arg-type]
    request = HttpRequest(method="GET", url="https://example.org")

    response = await adapter.send(request)

    assert response.content == b"ok"


@pytest.mark.asyncio
async def test__httpx_client_adapter__stream_success() -> None:
    client = httpx.AsyncClient(transport=_OkTransport())
    adapter = HttpxClientAdapter(client)
    request = HttpRequest(method="GET", url="https://example.org")

    async with adapter.stream(request) as response:
        data = await response.read()

    assert data == b"ok"
    await client.aclose()


@pytest.mark.asyncio
async def test__httpx_client_adapter__stream_timeout() -> None:
    client = httpx.AsyncClient(transport=_TimeoutTransport())
    adapter = HttpxClientAdapter(client)
    request = HttpRequest(method="GET", url="https://example.org")

    with pytest.raises(HttpTimeoutError):
        async with adapter.stream(request):
            pass

    await client.aclose()


@pytest.mark.asyncio
async def test__httpx_client_adapter__stream_transport_error() -> None:
    client = httpx.AsyncClient(transport=_ErrorTransport())
    adapter = HttpxClientAdapter(client)
    request = HttpRequest(method="GET", url="https://example.org")

    with pytest.raises(HttpTransportError):
        async with adapter.stream(request):
            pass

    await client.aclose()
