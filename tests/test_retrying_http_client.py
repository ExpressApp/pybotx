import pytest

from pybotx.domain.ports.http_client import HttpRequest
from pybotx.infrastructure.retrying_http_client import RetryingHttpClient


class _DummyResponse:
    def __init__(self, label: str) -> None:
        self.label = label


class _DummyStream:
    def __init__(self, response: _DummyResponse, tracker: dict[str, bool]) -> None:
        self._response = response
        self._tracker = tracker

    async def __aenter__(self):
        self._tracker["entered"] = True
        return self._response

    async def __aexit__(self, exc_type, exc, tb):
        self._tracker["exited"] = True
        return False


class _DummyClient:
    def __init__(self) -> None:
        self.request_calls = []
        self.stream_calls = []
        self.closed = False
        self.stream_tracker: dict[str, bool] | None = None

    async def send(self, request):  # type: ignore[no-untyped-def]
        self.request_calls.append(request)
        return _DummyResponse("request")

    def stream(self, request):  # type: ignore[no-untyped-def]
        self.stream_calls.append(request)
        tracker: dict[str, bool] = {}
        self.stream_tracker = tracker
        return _DummyStream(_DummyResponse("stream"), tracker)

    async def aclose(self) -> None:
        self.closed = True


class _SpyRetryPolicy:
    def __init__(self) -> None:
        self.calls = 0

    async def execute(self, func):  # type: ignore[no-untyped-def]
        self.calls += 1
        return await func()


class _FailRetryPolicy:
    async def execute(self, func):  # type: ignore[no-untyped-def]
        raise AssertionError("retry policy should not be called")


@pytest.mark.asyncio
async def test__retrying_http_client__request_uses_retry_policy() -> None:
    client = _DummyClient()
    policy = _SpyRetryPolicy()
    retrying = RetryingHttpClient(client=client, retry_policy=policy, enabled=True)

    response = await retrying.send(HttpRequest(method="GET", url="https://example.com"))

    assert response.label == "request"
    assert client.request_calls
    assert policy.calls == 1


@pytest.mark.asyncio
async def test__retrying_http_client__request_skips_retry_when_disabled() -> None:
    client = _DummyClient()
    policy = _FailRetryPolicy()
    retrying = RetryingHttpClient(client=client, retry_policy=policy, enabled=False)

    response = await retrying.send(HttpRequest(method="GET", url="https://example.com"))

    assert response.label == "request"
    assert client.request_calls


@pytest.mark.asyncio
async def test__retrying_http_client__stream_skips_retry_when_disabled() -> None:
    client = _DummyClient()
    policy = _FailRetryPolicy()
    retrying = RetryingHttpClient(
        client=client,
        retry_policy=policy,
        enabled=True,
        retry_stream=False,
    )

    async with retrying.stream(
        HttpRequest(method="GET", url="https://example.com")
    ) as response:
        assert response.label == "stream"

    assert client.stream_calls
    assert client.stream_tracker == {"entered": True, "exited": True}


@pytest.mark.asyncio
async def test__retrying_http_client__stream_uses_retry_policy() -> None:
    client = _DummyClient()
    policy = _SpyRetryPolicy()
    retrying = RetryingHttpClient(client=client, retry_policy=policy, enabled=True)

    async with retrying.stream(
        HttpRequest(method="GET", url="https://example.com")
    ) as response:
        assert response.label == "stream"

    assert client.stream_calls
    assert client.stream_tracker == {"entered": True, "exited": True}
    assert policy.calls == 1


@pytest.mark.asyncio
async def test__retrying_http_client__aclose_delegates() -> None:
    client = _DummyClient()
    policy = _SpyRetryPolicy()
    retrying = RetryingHttpClient(client=client, retry_policy=policy)

    await retrying.aclose()

    assert client.closed is True
