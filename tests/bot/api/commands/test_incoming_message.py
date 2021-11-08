from datetime import datetime
from typing import Callable, Optional
from uuid import UUID

import pytest

from botx import (
    Bot,
    Chat,
    ChatTypes,
    ClientPlatforms,
    ExpressApp,
    HandlerCollector,
    IncomingMessage,
    UserDevice,
    UserEventSender,
    lifespan_wrapper,
)
from botx.bot.models.commands.entities import Forward, Mention, Reply
from botx.bot.models.commands.enums import AttachmentTypes, MentionTypes
from botx.shared_models.domain.files import Image


@pytest.mark.asyncio
async def test__async_execute_raw_bot_command__minimally_filled_incoming_message() -> None:
    # - Arrange -
    payload = {
        "bot_id": "c1b0c5df-075c-55ff-a931-bfa39ddfd424",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {},
            "metadata": {},
        },
        "attachments": [],
        "async_files": [],
        "entities": [],
        "source_sync_id": None,
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": None,
            "ad_login": None,
            "app_version": None,
            "chat_type": "chat",
            "device": None,
            "device_meta": {
                "permissions": None,
                "pushes": False,
                "timezone": "Europe/Moscow",
            },
            "device_software": None,
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": None,
        },
        "proto_version": 4,
    }

    collector = HandlerCollector()
    incoming_message: Optional[IncomingMessage] = None

    @collector.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        nonlocal incoming_message
        incoming_message = message
        # Drop `raw_command` from asserting
        incoming_message.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert incoming_message == IncomingMessage(
        bot_id=UUID("c1b0c5df-075c-55ff-a931-bfa39ddfd424"),
        sync_id=UUID("6f40a492-4b5f-54f3-87ee-77126d825b51"),
        source_sync_id=None,
        body="/hello",
        data={},
        metadata={},
        sender=UserEventSender(
            huid=UUID("f16cdc5f-6366-5552-9ecd-c36290ab3d11"),
            ad_login=None,
            ad_domain=None,
            username=None,
            is_chat_admin=True,
            is_chat_creator=True,
            locale="en",
            device=UserDevice(
                manufacturer=None,
                name=None,
                os=None,
            ),
            express_app=ExpressApp(
                pushes=False,
                timezone="Europe/Moscow",
                permissions=None,
                platform=None,
                platform_package_id=None,
                version=None,
            ),
        ),
        chat=Chat(
            id=UUID("30dc1980-643a-00ad-37fc-7cc10d74e935"),
            type=ChatTypes.PERSONAL_CHAT,
            host="cts.example.com",
        ),
        raw_command=None,
    )


@pytest.mark.asyncio
async def test__async_execute_raw_bot_command__maximum_filled_incoming_message(
    datetime_formatter: Callable[[str], datetime],
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "c1b0c5df-075c-55ff-a931-bfa39ddfd424",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {"message": "data"},
            "metadata": {"message": "metadata"},
        },
        "attachments": [],
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
                "file_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
            },
        ],
        "entities": [
            {
                "type": "reply",
                "data": {
                    "source_sync_id": "a7ffba12-8d0a-534e-8896-a0aa2d93a434",
                    "sender": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                    "body": "все равно документацию никто не читает...",
                    "mentions": [],
                    "attachment": None,
                    "reply_type": "chat",
                    "source_group_chat_id": "918da23a-1c9a-506e-8a6f-1328f1499ee8",
                    "source_chat_name": "Serious Dev Chat",
                },
            },
            {
                "type": "forward",
                "data": {
                    "group_chat_id": "918da23a-1c9a-506e-8a6f-1328f1499ee8",
                    "sender_huid": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                    "forward_type": "chat",
                    "source_chat_name": "Simple Chat",
                    "source_sync_id": "a7ffba12-8d0a-534e-8896-a0aa2d93a434",
                    "source_inserted_at": "2020-04-21T22:09:32.178Z",
                },
            },
            {
                "type": "mention",
                "data": {
                    "mention_type": "contact",
                    "mention_id": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                    "mention_data": {
                        "user_huid": "ab103983-6001-44e9-889e-d55feb295494",
                        "name": "Вася Иванов",
                        "conn_type": "cts",
                    },
                },
            },
        ],
        "source_sync_id": "bc3d06ed-7b2e-41ad-99f9-ca28adc2c88d",
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": "domain",
            "ad_login": "login",
            "app_version": "1.21.9",
            "chat_type": "chat",
            "device": "Firefox 91.0",
            "device_meta": {
                "permissions": {
                    "microphone": True,
                    "notifications": False,
                },
                "pushes": False,
                "timezone": "Europe/Moscow",
            },
            "device_software": "Linux",
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": True,
            "is_creator": True,
            "locale": "en",
            "manufacturer": "Mozilla",
            "platform": "web",
            "platform_package_id": "ru.unlimitedtech.express",
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": "Ivanov Ivan Ivanovich",
        },
        "proto_version": 4,
    }

    collector = HandlerCollector()
    incoming_message: Optional[IncomingMessage] = None

    @collector.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        nonlocal incoming_message
        incoming_message = message
        # Drop `raw_command` from asserting
        incoming_message.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert incoming_message == IncomingMessage(
        bot_id=UUID("c1b0c5df-075c-55ff-a931-bfa39ddfd424"),
        sync_id=UUID("6f40a492-4b5f-54f3-87ee-77126d825b51"),
        source_sync_id=UUID("bc3d06ed-7b2e-41ad-99f9-ca28adc2c88d"),
        body="/hello",
        data={"message": "data"},
        metadata={"message": "metadata"},
        sender=UserEventSender(
            huid=UUID("f16cdc5f-6366-5552-9ecd-c36290ab3d11"),
            ad_login="login",
            ad_domain="domain",
            username="Ivanov Ivan Ivanovich",
            is_chat_admin=True,
            is_chat_creator=True,
            locale="en",
            device=UserDevice(
                manufacturer="Mozilla",
                name="Firefox 91.0",
                os="Linux",
            ),
            express_app=ExpressApp(
                pushes=False,
                timezone="Europe/Moscow",
                permissions={"microphone": True, "notifications": False},
                platform=ClientPlatforms.WEB,
                platform_package_id="ru.unlimitedtech.express",
                version="1.21.9",
            ),
        ),
        chat=Chat(
            id=UUID("30dc1980-643a-00ad-37fc-7cc10d74e935"),
            type=ChatTypes.PERSONAL_CHAT,
            host="cts.example.com",
        ),
        raw_command=None,
        file=Image(
            type=AttachmentTypes.IMAGE,
            filename="pass.png",
            size=1502345,
            is_async_file=True,
            _file_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
        ),
        mentions=[
            Mention(
                type=MentionTypes.CONTACT,
                huid=UUID("ab103983-6001-44e9-889e-d55feb295494"),
                name="Вася Иванов",
            ),
        ],
        forward=Forward(
            chat_id=UUID("918da23a-1c9a-506e-8a6f-1328f1499ee8"),
            huid=UUID("c06a96fa-7881-0bb6-0e0b-0af72fe3683f"),
            type=ChatTypes.PERSONAL_CHAT,
            chat_name="Simple Chat",
            sync_id=UUID("a7ffba12-8d0a-534e-8896-a0aa2d93a434"),
            created_at=datetime_formatter("2020-04-21T22:09:32.178Z"),
        ),
        reply=Reply(
            chat_id=UUID("918da23a-1c9a-506e-8a6f-1328f1499ee8"),
            huid=UUID("c06a96fa-7881-0bb6-0e0b-0af72fe3683f"),
            type=ChatTypes.PERSONAL_CHAT,
            chat_name="Serious Dev Chat",
            sync_id=UUID("a7ffba12-8d0a-534e-8896-a0aa2d93a434"),
            body="все равно документацию никто не читает...",
        ),
    )
