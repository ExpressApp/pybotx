from typing import Optional
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
async def test__async_execute_raw_bot_command__maximum_filled_incoming_message() -> None:
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
        "async_files": [],
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
    )
