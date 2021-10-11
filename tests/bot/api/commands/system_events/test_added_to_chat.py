from typing import Optional
from uuid import UUID

import pytest

from botx import Bot, HandlerCollector, lifespan_wrapper
from botx.bot.models.commands.system_events.added_to_chat import AddedToChatEvent


@pytest.mark.asyncio
async def test__added_to_chat__succeed() -> None:
    # - Arrange -
    payload = {
        "bot_id": "bc7f96e2-91a5-5de4-8bde-23765450cac8",
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

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert added_to_chat == AddedToChatEvent(
        huids=[
            UUID("ab103983-6001-44e9-889e-d55feb295494"),
            UUID("dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4"),
        ],
        bot_id=UUID("bc7f96e2-91a5-5de4-8bde-23765450cac8"),
        raw_command=None,
    )
