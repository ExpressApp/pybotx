from typing import Optional
from uuid import UUID

import pytest

from botx import (
    Bot,
    Chat,
    ChatCreatedEvent,
    ChatCreatedMember,
    ChatTypes,
    ClientPlatforms,
    ExpressApp,
    HandlerCollector,
    IncomingMessage,
    UserDevice,
    UserEventSender,
    UserKinds,
)
from botx.testing import lifespan_wrapper


@pytest.mark.asyncio
async def test_minimally_filled_incoming_message() -> None:
    # - Arrange -
    payload = """{
        "bot_id": "c1b0c5df-075c-55ff-a931-bfa39ddfd424",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {},
            "metadata": {}
        },
        "source_sync_id": null,
        "sync_id": "6f40a492-4b5f-54f3-87ee-77126d825b51",
        "from": {
            "ad_domain": null,
            "ad_login": null,
            "app_version": null,
            "chat_type": "chat",
            "device": null,
            "device_meta": {
                "permissions": null,
                "pushes": false,
                "timezone": "Europe/Moscow"
            },
            "device_software": null,
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": true,
            "is_creator": true,
            "locale": "en",
            "manufacturer": null,
            "platform": null,
            "platform_package_id": null,
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": null
        }
    }
    """

    collector = HandlerCollector()
    incoming_message: Optional[IncomingMessage] = None

    @collector.default
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        nonlocal incoming_message
        incoming_message = message
        # Drop `raw_command` from asserting
        incoming_message.raw_command = None

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_botx_command(payload)

    # - Assert -
    assert incoming_message == IncomingMessage(
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
            bot_id=UUID("c1b0c5df-075c-55ff-a931-bfa39ddfd424"),
            type=ChatTypes.PERSONAL_CHAT,
            host="cts.example.com",
        ),
        raw_command=None,
    )


@pytest.mark.asyncio
async def test_maximum_filled_incoming_message() -> None:
    # - Arrange -
    payload = """{
        "bot_id": "c1b0c5df-075c-55ff-a931-bfa39ddfd424",
        "command": {
            "body": "/hello",
            "command_type": "user",
            "data": {"message": "data"},
            "metadata": {"message": "metadata"}
        },
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
                    "microphone": true,
                    "notifications": false
                },
                "pushes": false,
                "timezone": "Europe/Moscow"
            },
            "device_software": "Linux",
            "group_chat_id": "30dc1980-643a-00ad-37fc-7cc10d74e935",
            "host": "cts.example.com",
            "is_admin": true,
            "is_creator": true,
            "locale": "en",
            "manufacturer": "Mozilla",
            "platform": "web",
            "platform_package_id": "ru.unlimitedtech.express",
            "user_huid": "f16cdc5f-6366-5552-9ecd-c36290ab3d11",
            "username": "Ivanov Ivan Ivanovich"
        }
    }
    """

    collector = HandlerCollector()
    incoming_message: Optional[IncomingMessage] = None

    @collector.default
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        nonlocal incoming_message
        incoming_message = message
        # Drop `raw_command` from asserting
        incoming_message.raw_command = None

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_botx_command(payload)

    # - Assert -
    assert incoming_message == IncomingMessage(
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
            bot_id=UUID("c1b0c5df-075c-55ff-a931-bfa39ddfd424"),
            type=ChatTypes.PERSONAL_CHAT,
            host="cts.example.com",
        ),
        raw_command=None,
    )


@pytest.mark.asyncio
async def test_chat_created() -> None:
    # - Arrange -
    payload = """{
        "bot_id": "bc7f96e2-91a5-5de4-8bde-23765450cac8",
        "command": {
            "body": "system:chat_created",
            "command_type": "system",
            "data": {
                "chat_type": "group_chat",
                "creator": "83fbf1c7-f14b-5176-bd32-ca15cf00d4b7",
                "group_chat_id": "dea55ee4-7a9f-5da0-8c73-079f400ee517",
                "members": [
                    {
                        "admin": true,
                        "huid": "bc7f96e2-91a5-5de4-8bde-23765450cac8",
                        "name": "Feature bot",
                        "user_kind": "botx"
                    },
                    {
                        "admin": false,
                        "huid": "83fbf1c7-f14b-5176-bd32-ca15cf00d4b7",
                        "name": "Ivanov Ivan Ivanovich",
                        "user_kind": "cts_user"
                    }
                ],
                "name": "Feature-party"
            },
            "metadata": {}
        },
        "source_sync_id": null,
        "sync_id": "2c1a31d6-f47f-5f54-aee2-d0c526bb1d54",
        "from": {
            "ad_domain": null,
            "ad_login": null,
            "app_version": null,
            "chat_type": "group_chat",
            "device": null,
            "device_meta": {
                "permissions": null,
                "pushes": null,
                "timezone": null
            },
            "device_software": null,
            "group_chat_id": "dea55ee4-7a9f-5da0-8c73-079f400ee517",
            "host": "cts.example.com",
            "is_admin": null,
            "is_creator": null,
            "locale": "en",
            "manufacturer": null,
            "platform": null,
            "platform_package_id": null,
            "user_huid": null,
            "username": null
        }
    }
    """

    collector = HandlerCollector()
    chat_created: Optional[ChatCreatedEvent] = None

    @collector.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
        nonlocal chat_created
        chat_created = event
        # Drop `raw_command` from asserting
        chat_created.raw_command = None

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_botx_command(payload)

    # - Assert -
    assert chat_created == ChatCreatedEvent(
        sync_id=UUID("2c1a31d6-f47f-5f54-aee2-d0c526bb1d54"),
        chat_id=UUID("dea55ee4-7a9f-5da0-8c73-079f400ee517"),
        bot_id=UUID("bc7f96e2-91a5-5de4-8bde-23765450cac8"),
        host="cts.example.com",
        chat_name="Feature-party",
        chat_type=ChatTypes.GROUP_CHAT,
        creator_id=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
        members=[
            ChatCreatedMember(
                is_admin=True,
                huid=UUID("bc7f96e2-91a5-5de4-8bde-23765450cac8"),
                username="Feature bot",
                kind=UserKinds.BOT,
            ),
            ChatCreatedMember(
                is_admin=False,
                huid=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
                username="Ivanov Ivan Ivanovich",
                kind=UserKinds.CTS_USER,
            ),
        ],
        raw_command=None,
    )
