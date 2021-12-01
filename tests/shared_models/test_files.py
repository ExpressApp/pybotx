from http import HTTPStatus
from typing import Any, Callable, Dict, Optional
from uuid import UUID

import httpx
import pytest
import respx

from botx import Bot, BotAccount, HandlerCollector, IncomingMessage, lifespan_wrapper


@respx.mock
@pytest.mark.asyncio
async def test__async_file__open(
    httpx_client: httpx.AsyncClient,
    chat_id: UUID,
    host: str,
    file_id: UUID,
    bot_account: BotAccount,
    bot_id: UUID,
    incoming_message_payload_factory: Callable[..., Dict[str, Any]],
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

    payload = incoming_message_payload_factory(
        bot_id=bot_id,
        async_file={
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
            "file_id": str(file_id),
        },
        group_chat_id=chat_id,
        host=host,
    )

    collector = HandlerCollector()
    read_content: Optional[bytes] = None

    @collector.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        nonlocal read_content

        assert message.file
        async with message.file.open() as fo:
            read_content = await fo.read()

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        httpx_client=httpx_client,
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert read_content == b"Hello, world!\n"
    assert endpoint.called
