from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from aiofiles.tempfile import NamedTemporaryFile
from respx.router import MockRouter

from pybotx import BotAccountWithSecret, InvalidBotXStatusCodeError
from pybotx.async_buffer import AsyncBufferWritable
from pybotx.bot.bot_accounts_storage import BotAccountsStorage
from pybotx.client.botx_method import BotXMethod, response_exception_thrower
from pybotx.client.exceptions.base import BaseClientError
from tests.client.test_botx_method import BotXAPIFooBarRequestPayload


class FooBarError(BaseClientError):
    """Test exception."""


class FooBarStreamMethod(BotXMethod):
    status_handlers = {
        403: response_exception_thrower(FooBarError),
    }

    async def execute(
        self,
        payload: BotXAPIFooBarRequestPayload,
        async_buffer: AsyncBufferWritable,
    ) -> None:
        path = "/foo/bar"

        async with self._botx_method_stream(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        ) as response:
            async for chunk in response.aiter_bytes():
                await async_buffer.write(chunk)

        await async_buffer.seek(0)


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__botx_method_stream__invalid_botx_status_code_error_raised(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(f"https://{host}/foo/bar", params={"baz": 1}).mock(
        return_value=httpx.Response(HTTPStatus.METHOD_NOT_ALLOWED),
    )

    method = FooBarStreamMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(InvalidBotXStatusCodeError) as exc:
        await method.execute(payload, async_buffer)

    # - Assert -
    assert "failed with code 405" in str(exc.value)
    assert endpoint.called


async def test__botx_method_stream__status_handler_called(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(f"https://{host}/foo/bar", params={"baz": 1}).mock(
        return_value=httpx.Response(HTTPStatus.FORBIDDEN),
    )

    method = FooBarStreamMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    with pytest.raises(FooBarError) as exc:
        await method.execute(payload, async_buffer)

    # - Assert -
    assert "403" in str(exc.value)
    assert endpoint.called


async def test__botx_method_stream__succeed(
    httpx_client: httpx.AsyncClient,
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(f"https://{host}/foo/bar", params={"baz": 1}).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            content=b"Hello, world!\n",
        ),
    )

    method = FooBarStreamMethod(
        bot_id,
        httpx_client,
        BotAccountsStorage([bot_account]),
    )
    payload = BotXAPIFooBarRequestPayload.from_domain(baz=1)

    # - Act -
    await method.execute(payload, async_buffer)

    # - Assert -
    assert await async_buffer.read() == b"Hello, world!\n"
    assert endpoint.called
