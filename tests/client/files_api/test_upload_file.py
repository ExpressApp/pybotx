from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx
from aiofiles.tempfile import NamedTemporaryFile

from botx import Bot, BotAccount, HandlerCollector, lifespan_wrapper


@respx.mock
@pytest.mark.asyncio
async def test__download_file__succeed(
    httpx_client: httpx.AsyncClient,
    host: str,
    bot_id: UUID,
    chat_id: UUID,
    file_id: UUID,
    bot_account: BotAccount,
    async_buffer: NamedTemporaryFile,
    mock_authorization: None,
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
