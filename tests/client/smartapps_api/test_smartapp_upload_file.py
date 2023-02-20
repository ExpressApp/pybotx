from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
from aiofiles.tempfile import NamedTemporaryFile
from respx.router import MockRouter

from pybotx import Bot, BotAccountWithSecret, HandlerCollector, lifespan_wrapper
from pybotx.client.exceptions.files import FileTypeNotAllowed

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__upload_static_file__wrong_file_type(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    await async_buffer.write(b"Hello, world!\n")
    await async_buffer.seek(0)

    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/smartapps/upload_file",
        # TODO: check data too, when files pattern will be ready
        # https://github.com/lundberg/respx/issues/115
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.BAD_REQUEST,
            json={
                "status": "error",
                "reason": "invalid_extension",
                "errors": [],
                "error_data": {
                    "allowed": ["jpg", "jpeg", "gif", "png", "svg", "tiff"],
                    "error_descrion": "txt extension isn't allowed for unencrypted smartapp files",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(FileTypeNotAllowed) as exc:
            await bot.upload_static_file(
                bot_id=bot_id,
                async_buffer=async_buffer,
                filename="test.txt",
            )

    # - Assert -
    assert endpoint.called
    assert "txt" in str(exc.value)


async def test__upload_static_file__succeed(
    respx_mock: MockRouter,
    host: str,
    bot_id: UUID,
    bot_account: BotAccountWithSecret,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    await async_buffer.write(b"Hello, world!\n")
    await async_buffer.seek(0)

    endpoint = respx_mock.post(
        f"https://{host}/api/v3/botx/smartapps/upload_file",
        # TODO: check data too, when files pattern will be ready
        # https://github.com/lundberg/respx/issues/115
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "link": "https://link.to/file",
                },
            },
        ),
    )

    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        smartapp_file_link = await bot.upload_static_file(
            bot_id=bot_id,
            async_buffer=async_buffer,
            filename="test.png",
        )

    # - Assert -
    assert endpoint.called
    assert smartapp_file_link == "https://link.to/file"
