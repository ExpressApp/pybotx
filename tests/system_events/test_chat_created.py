from typing import Optional
from uuid import UUID

import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    Chat,
    ChatCreatedEvent,
    ChatCreatedMember,
    ChatTypes,
    HandlerCollector,
    UserKinds,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__chat_created__succeed(
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
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
                        "huid": "24348246-6791-4ac0-9d86-b948cd6a0e46",
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

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert chat_created == ChatCreatedEvent(
        sync_id=UUID("2c1a31d6-f47f-5f54-aee2-d0c526bb1d54"),
        bot_id=UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
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
                huid=UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
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
