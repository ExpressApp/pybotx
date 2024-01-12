from typing import Optional
from uuid import UUID

import pytest

from pybotx import (
    Bot,
    BotAccount,
    BotAccountWithSecret,
    EventEdit,
    HandlerCollector,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__event_edit__succeed(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = {
        "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
        "command": {
            "body": "system:event_edit",
            "data": {"body": "Edited"},
            "command_type": "system",
            "metadata": {},
        },
        "async_files": [],
        "attachments": [],
        "entities": [],
        "from": {
            "user_huid": None,
            "group_chat_id": None,
            "ad_login": None,
            "ad_domain": None,
            "username": None,
            "chat_type": None,
            "manufacturer": None,
            "device": None,
            "device_software": None,
            "device_meta": {},
            "platform": None,
            "platform_package_id": None,
            "is_admin": None,
            "is_creator": None,
            "app_version": None,
            "locale": "en",
            "host": "cts.example.com",
        },
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "proto_version": 4,
        "source_sync_id": None,
    }

    collector = HandlerCollector()
    event_edit: Optional[EventEdit] = None

    @collector.event_edit
    async def event_edit_handler(event: EventEdit, bot: Bot) -> None:
        nonlocal event_edit
        event_edit = event
        # Drop `raw_command` from asserting
        event_edit.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert event_edit == EventEdit(
        bot=BotAccount(
            id=UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
            host="cts.example.com",
        ),
        raw_command=None,
        body="Edited",
    )
