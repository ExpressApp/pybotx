from typing import Optional
from uuid import UUID

import pytest
import respx

from botx import (
    AddedToChatEvent,
    Bot,
    BotAccount,
    BotAccountWithSecret,
    Chat,
    ChatTypes,
    HandlerCollector,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__added_to_chat__succeed(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "command": {
            "body": "system:added_to_chat",
            "command_type": "system",
            "data": {
                "added_members": [
                    "ab103983-6001-44e9-889e-d55feb295494",
                    "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                ],
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
    added_to_chat: Optional[AddedToChatEvent] = None

    @collector.added_to_chat
    async def added_to_chat_handler(event: AddedToChatEvent, bot: Bot) -> None:
        nonlocal added_to_chat
        added_to_chat = event
        # Drop `raw_command` from asserting
        added_to_chat.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert added_to_chat == AddedToChatEvent(
        bot=BotAccount(
            id=UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
            host="cts.example.com",
        ),
        raw_command=None,
        huids=[
            UUID("ab103983-6001-44e9-889e-d55feb295494"),
            UUID("dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4"),
        ],
        chat=Chat(
            id=UUID("dea55ee4-7a9f-5da0-8c73-079f400ee517"),
            type=ChatTypes.GROUP_CHAT,
        ),
    )
