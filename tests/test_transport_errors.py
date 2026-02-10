import os
from uuid import UUID

import pytest

from pybotx.domain.errors import TransportError
from pybotx.domain.ports.http_client import HttpTransportError
from pybotx.infrastructure.botx_api import HttpBotXApi
from pybotx.infrastructure.client.botx_method import BotXMethod


class DummyHttpClient:
    async def send(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise HttpTransportError("boom")

    def stream(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise HttpTransportError("boom")

    async def aclose(self) -> None:
        return None


class DummyBuffer:
    async def write(self, content: bytes) -> int:
        return len(content)

    async def seek(self, cursor: int, whence: int = os.SEEK_SET) -> int:
        return 0

    async def tell(self) -> int:
        return 0


@pytest.mark.asyncio
async def test__botx_method__http_error_converted_to_transport_error() -> None:
    method = BotXMethod(
        UUID("00000000-0000-0000-0000-000000000001"),
        DummyHttpClient(),
        object(),
        None,
    )

    with pytest.raises(TransportError):
        await method._botx_method_call("GET", "https://example.com")


@pytest.mark.asyncio
async def test__http_botx_api__download_url_transport_error() -> None:
    api = HttpBotXApi(
        http_client=DummyHttpClient(),
        bot_accounts_storage=object(),
        callbacks_manager=object(),
    )

    with pytest.raises(TransportError):
        await api.download_url(url="https://example.com", async_buffer=DummyBuffer())


@pytest.mark.asyncio
async def test__botx_method__stream_http_error_converted_to_transport_error() -> None:
    method = BotXMethod(
        UUID("00000000-0000-0000-0000-000000000002"),
        DummyHttpClient(),
        object(),
        None,
    )

    with pytest.raises(TransportError):
        async with method._botx_method_stream("GET", "https://example.com"):
            pass
