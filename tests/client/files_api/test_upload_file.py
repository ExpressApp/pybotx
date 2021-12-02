from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx
from aiofiles.tempfile import NamedTemporaryFile

from botx import Bot, BotAccount, ChatNotFoundError, HandlerCollector, lifespan_wrapper


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__download_file__chat_not_found_error_raised(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    chat_id: UUID,
    file_id: UUID,
    bot_account: BotAccount,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    await async_buffer.write(b"Hello, world!\n")
    await async_buffer.seek(0)

    endpoint = respx.post(
        f"https://{host}/api/v3/botx/files/upload",
        # TODO: check data too, when files pattern will be ready
        # https://github.com/lundberg/respx/issues/115
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NOT_FOUND,
            json={
                "status": "error",
                "reason": "chat_not_found",
                "errors": [],
                "error_data": {
                    "group_chat_id": "84a12e71-3efc-5c34-87d5-84e3d9ad64fd",
                    "error_description": "Chat with id 84a12e71-3efc-5c34-87d5-84e3d9ad64fd not found",
                },
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ChatNotFoundError) as exc:
            await bot.upload_file(bot_id, chat_id, async_buffer, "test.txt")

    # - Assert -
    assert "chat_not_found" in str(exc.value)
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__download_file__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    chat_id: UUID,
    file_id: UUID,
    bot_account: BotAccount,
    async_buffer: NamedTemporaryFile,
) -> None:
    # - Arrange -
    await async_buffer.write(b"Hello, world!\n")
    await async_buffer.seek(0)

    endpoint = respx.post(
        f"https://{host}/api/v3/botx/files/upload",
        # TODO: check data too, when files pattern will be ready
        # https://github.com/lundberg/respx/issues/115
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            json={
                "status": "ok",
                "result": {
                    "type": "image",
                    "file": "https://link.to/file",
                    "file_mime_type": "image/png",
                    "file_name": "pass.png",
                    "file_preview": "https://link.to/preview",
                    "file_preview_height": 300,
                    "file_preview_width": 300,
                    "file_size": 1502345,
                    "file_hash": "Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
                    "file_encryption_algo": "stream",
                    "chunk_size": 2097152,
                    "file_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                    "caption": "текст",
                    "duration": None,
                },
            },
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.upload_file(bot_id, chat_id, async_buffer, "test.txt")

    # - Assert -
    assert endpoint.called
