from http import HTTPStatus
from typing import Any, Callable, Dict, Optional
from uuid import UUID

import httpx
import pytest
from respx.router import MockRouter

from pybotx import (
    AttachmentTypes,
    Bot,
    BotAccountWithSecret,
    Document,
    File,
    HandlerCollector,
    Image,
    Video,
    Voice,
    lifespan_wrapper,
)
from pybotx.models.system_events.smartapp_event import SmartAppEvent

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__async_file__open(
    respx_mock: MockRouter,
    host: str,
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
) -> None:
    # - Arrange -
    endpoint = respx_mock.get(
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

    payload = {
        "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
        "command": {
            "body": "system:smartapp_event",
            "data": {
                "ref": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                "smartapp_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                "data": {
                    "type": "smartapp_rpc",
                    "method": "folders.get",
                    "params": {
                        "q": 1,
                    },
                },
                "opts": {"option": "test_option"},
                "smartapp_api_version": 1,
            },
            "command_type": "system",
            "metadata": {},
        },
        "async_files": [
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
                "file_id": "c3b9def2-b2c8-4732-b61f-99b9b110fa80",
            },
        ],
        "attachments": [],
        "entities": [],
        "from": {
            "user_huid": "b9197d3a-d855-5d34-ba8a-eff3a975ab20",
            "group_chat_id": "054af49e-5e18-4dca-ad73-4f96b6de63fa",
            "host": host,
            "ad_login": None,
            "ad_domain": None,
            "username": None,
            "chat_type": "group_chat",
            "manufacturer": None,
            "device": None,
            "device_software": None,
            "device_meta": {},
            "platform": None,
            "platform_package_id": None,
            "is_admin": False,
            "is_creator": False,
            "app_version": None,
            "locale": "en",
        },
        "bot_id": str(bot_id),
        "proto_version": 4,
        "source_sync_id": None,
    }

    collector = HandlerCollector()
    read_content: Optional[bytes] = None

    @collector.smartapp_event
    async def smartapp_event_handler(event: SmartAppEvent, bot: Bot) -> None:
        nonlocal read_content

        assert event.files
        async with event.files[0].open() as fo:
            read_content = await fo.read()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload, verify_request=False)

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


@pytest.mark.parametrize(
    "api_async_file,domain_async_file",
    API_AND_DOMAIN_FILES,
)
async def test__async_execute_raw_bot_command__different_file_types(
    api_async_file: Dict[str, Any],
    domain_async_file: File,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = {
        "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
        "command": {
            "body": "system:smartapp_event",
            "data": {
                "ref": "6fafda2c-6505-57a5-a088-25ea5d1d0364",
                "smartapp_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                "data": {
                    "type": "smartapp_rpc",
                    "method": "folders.get",
                    "params": {
                        "q": 1,
                    },
                },
                "opts": {"option": "test_option"},
                "smartapp_api_version": 1,
            },
            "command_type": "system",
            "metadata": {},
        },
        "async_files": [api_async_file],
        "attachments": [],
        "entities": [],
        "from": {
            "user_huid": "b9197d3a-d855-5d34-ba8a-eff3a975ab20",
            "group_chat_id": "dea55ee4-7a9f-5da0-8c73-079f400ee517",
            "host": "cts.example.com",
            "ad_login": None,
            "ad_domain": None,
            "username": None,
            "chat_type": "group_chat",
            "manufacturer": None,
            "device": None,
            "device_software": None,
            "device_meta": {},
            "platform": None,
            "platform_package_id": None,
            "is_admin": False,
            "is_creator": False,
            "app_version": None,
            "locale": "en",
        },
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "proto_version": 4,
        "source_sync_id": None,
    }

    collector = HandlerCollector()
    smartapp_event: Optional[SmartAppEvent] = None

    @collector.smartapp_event
    async def smartapp_event_handler(event: SmartAppEvent, bot: Bot) -> None:
        nonlocal smartapp_event
        smartapp_event = event
        # Drop `raw_command` from asserting
        smartapp_event.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert smartapp_event
    assert smartapp_event.files == [domain_async_file]
