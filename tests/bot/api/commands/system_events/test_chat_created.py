from typing import Optional
from uuid import UUID

import pytest

from botx import (
    Bot,
    Chat,
    ChatCreatedEvent,
    ChatCreatedMember,
    ChatTypes,
    HandlerCollector,
    UserKinds,
    lifespan_wrapper,
)


@pytest.mark.asyncio
async def test__chat_created__succeed() -> None:
    # - Arrange -
    payload = {
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
                        "admin": True,
                        "huid": "bc7f96e2-91a5-5de4-8bde-23765450cac8",
                        "name": "Feature bot",
                        "user_kind": "botx",
                    },
                    {
                        "admin": False,
                        "huid": "83fbf1c7-f14b-5176-bd32-ca15cf00d4b7",
                        "name": "Ivanov Ivan Ivanovich",
                        "user_kind": "cts_user",
                    },
                ],
                "name": "Feature-party",
            },
            "metadata": {},
        },
        "source_sync_id": None,
        "sync_id": "2c1a31d6-f47f-5f54-aee2-d0c526bb1d54",
        "from": {
            "ad_domain": None,
            "ad_login": None,
            "app_version": None,
            "chat_type": "group_chat",
            "device": None,
            "device_meta": {
                "permissions": None,
                "pushes": None,
                "timezone": None,
            },
            "device_software": None,
            "group_chat_id": "dea55ee4-7a9f-5da0-8c73-079f400ee517",
            "host": "cts.example.com",
            "is_admin": None,
            "is_creator": None,
            "locale": "en",
            "manufacturer": None,
            "platform": None,
            "platform_package_id": None,
            "user_huid": None,
            "username": None,
        },
        "proto_version": 4,
    }

    collector = HandlerCollector()
    chat_created: Optional[ChatCreatedEvent] = None

    @collector.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
        nonlocal chat_created
        chat_created = event
        # Drop `raw_command` from asserting
        chat_created.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert chat_created == ChatCreatedEvent(
        sync_id=UUID("2c1a31d6-f47f-5f54-aee2-d0c526bb1d54"),
        bot_id=UUID("bc7f96e2-91a5-5de4-8bde-23765450cac8"),
        chat_name="Feature-party",
        chat=Chat(
            id=UUID("dea55ee4-7a9f-5da0-8c73-079f400ee517"),
            type=ChatTypes.GROUP_CHAT,
            host="cts.example.com",
        ),
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
