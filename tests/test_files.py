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
    host: str,
    bot_account: BotAccount,
    bot_id: UUID,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
) -> None:
    # - Arrange -
    endpoint = respx.get(
        f"https://{host}/api/v3/botx/files/download",
        params={
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "file_id": "c3b9def2-b2c8-4732-b61f-99b9b110fa80",
        },
        headers={"Authorization": "Bearer token"},
    ).mock(
        return_value=httpx.Response(
            HTTPStatus.OK,
            content=b"Hello, world!\n",
        ),
    )

    payload = api_incoming_message_factory(
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
            "file_id": "c3b9def2-b2c8-4732-b61f-99b9b110fa80",
        },
        group_chat_id="054af49e-5e18-4dca-ad73-4f96b6de63fa",
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
            _file_url="https://link.to/file",
            _file_mimetype="image/png",
            _file_hash="Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
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
            _file_url="https://link.to/file",
            _file_mimetype="video/mp4",
            _file_hash="Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
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
            _file_url="https://link.to/file",
            _file_mimetype="plain/text",
            _file_hash="Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
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
            _file_url="https://link.to/file",
            _file_mimetype="audio/mp3",
            _file_hash="Jd9r+OKpw5y+FSCg1xNTSUkwEo4nCW1Sn1AkotkOpH0=",
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
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    payload = api_incoming_message_factory(async_file=api_async_file)

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
