from http import HTTPStatus
from uuid import UUID

import httpx
import pytest
import respx
from aiofiles.tempfile import NamedTemporaryFile

from botx import Bot, BotAccount, HandlerCollector, lifespan_wrapper
from botx.client.files_api.exceptions import FileDeletedError


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
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/files/download",
        params={
            "group_chat_id": chat_id,
            "file_id": file_id,
        },
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            content=b"Hello, world!\n",
        ),
    )

    built_bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await bot.download_file(bot_id, chat_id, file_id, async_buffer)

    # - Assert -
    assert await async_buffer.read() == b"Hello, world!\n"
    assert endpoint.called


@respx.mock
@pytest.mark.asyncio
async def test__download_file__file_deleted_error_raised(
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
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/files/download",
        params={
            "group_chat_id": chat_id,
            "file_id": file_id,
        },
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.NO_CONTENT,
            json={
                "status": "error",
                "reason": "file_deleted",
                "errors": [],
                "error_data": {
                    "link": "/example/file.jpeg",
                    "error_description": "File at the specified link has been deleted",
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
        with pytest.raises(FileDeletedError) as exc:
            await bot.download_file(bot_id, chat_id, file_id, async_buffer)

    # - Assert -
    assert "file_deleted" in str(exc.value)
    assert endpoint.called
