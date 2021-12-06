from http import HTTPStatus
from typing import Any, Callable, Dict, Optional
from uuid import UUID

import httpx
import pytest
import respx

from botx import (
    AttachmentTypes,
    Bot,
    BotAccount,
    Document,
    File,
    HandlerCollector,
    Image,
    IncomingMessage,
    Video,
    Voice,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__async_file__open(
    httpx_client: httpx.AsyncClient,
    chat_id: UUID,
    host: str,
    file_id: UUID,
    bot_account: BotAccount,
    bot_id: UUID,
    incoming_message_payload_factory: Callable[..., Dict[str, Any]],
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


API_AND_DOMAIN_FILES = (
    (
        {
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
        },
        Image(
            type=AttachmentTypes.IMAGE,
            filename="pass.png",
            size=1502345,
            is_async_file=True,
            _file_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
        ),
    ),
    (
        {
            "type": "video",
            "file": "https://link.to/file",
            "file_mime_type": "video/mp4",
            "file_name": "pass.mp4",
            "file_preview": "https://link.to/preview",
            "file_preview_height": 300,
            "file_preview_width": 300,
            "file_size": 1502345,
            "file_hash": "Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
            "file_encryption_algo": "stream",
            "chunk_size": 2097152,
            "file_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
            "duration": 10,
        },
        Video(
            type=AttachmentTypes.VIDEO,
            filename="pass.mp4",
            size=1502345,
            is_async_file=True,
            duration=10,
            _file_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
        ),
    ),
    (
        {
            "type": "document",
            "file": "https://link.to/file",
            "file_mime_type": "plain/text",
            "file_name": "pass.txt",
            "file_preview": "https://link.to/preview",
            "file_preview_height": 300,
            "file_preview_width": 300,
            "file_size": 1502345,
            "file_hash": "Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
            "file_encryption_algo": "stream",
            "chunk_size": 2097152,
            "file_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
        },
        Document(
            type=AttachmentTypes.DOCUMENT,
            filename="pass.txt",
            size=1502345,
            is_async_file=True,
            _file_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
        ),
    ),
    (
        {
            "type": "voice",
            "file": "https://link.to/file",
            "file_mime_type": "audio/mp3",
            "file_name": "pass.mp3",
            "file_preview": "https://link.to/preview",
            "file_preview_height": 300,
            "file_preview_width": 300,
            "file_size": 1502345,
            "file_hash": "Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
            "file_encryption_algo": "stream",
            "chunk_size": 2097152,
            "file_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
            "duration": 10,
        },
        Voice(
            type=AttachmentTypes.VOICE,
            filename="pass.mp3",
            size=1502345,
            is_async_file=True,
            duration=10,
            _file_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
        ),
    ),
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
@pytest.mark.parametrize(
    "api_async_file,domain_async_file",
    API_AND_DOMAIN_FILES,
)
async def test__async_execute_raw_bot_command__different_file_types(
    api_async_file: Dict[str, Any],
    domain_async_file: File,
    incoming_message_payload_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    payload = incoming_message_payload_factory(async_file=api_async_file)

    collector = HandlerCollector()
    incoming_message: Optional[IncomingMessage] = None

    @collector.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        nonlocal incoming_message
        incoming_message = message
        # Drop `raw_command` from asserting
        incoming_message.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert incoming_message
    assert incoming_message.file == domain_async_file
