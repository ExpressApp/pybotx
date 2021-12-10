from typing import Optional
from uuid import UUID

import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    BotRecipient,
    Chat,
    ChatTypes,
    DeletedFromChatEvent,
    HandlerCollector,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__deleted_from_chat__succeed(
    bot_account: BotAccount,
) -> None:
    # - Arrange -
    payload = {
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "command": {
            "body": "system:deleted_from_chat",
            "command_type": "system",
            "data": {
                "deleted_members": [
                    "ab103983-6001-44e9-889e-d55feb295494",
                    "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                ],
            },
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
    deleted_from_chat: Optional[DeletedFromChatEvent] = None

    @collector.deleted_from_chat
    async def deleted_from_chat_handler(event: DeletedFromChatEvent, bot: Bot) -> None:
        nonlocal deleted_from_chat
        deleted_from_chat = event
        # Drop `raw_command` from asserting
        deleted_from_chat.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert deleted_from_chat == DeletedFromChatEvent(
        bot=BotRecipient(
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
