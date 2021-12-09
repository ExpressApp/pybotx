from typing import Optional
from uuid import UUID

import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    BotRecipient,
    HandlerCollector,
    SmartAppEvent,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__smartapp__succeed(
    bot_account: BotAccount,
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
        "async_files": [],
        "attachments": [],
        "entities": [],
        "from": {
            "user_huid": "b9197d3a-d855-5d34-ba8a-eff3a975ab20",
            "group_chat_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
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
            "host": "cts.example.com",
        },
        "bot_id": "24348246-6791-4ac0-9d86-b948cd6a0e46",
        "proto_version": 4,
        "source_sync_id": None,
    }

    collector = HandlerCollector()
    smartapp: Optional[SmartAppEvent] = None

    @collector.smartapp
    async def smartapp_handler(event: SmartAppEvent, bot: Bot) -> None:
        nonlocal smartapp
        smartapp = event
        # Drop `raw_command` from asserting
        smartapp.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload)

    # - Assert -
    assert smartapp == SmartAppEvent(
        bot=BotRecipient(
            id=UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
            host="cts.example.com",
        ),
        raw_command=None,
        smartapp_id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
        data={
            "type": "smartapp_rpc",
            "method": "folders.get",
            "params": {
                "q": 1,
            },
        },
        smartapp_api_version=1,
        opts={"option": "test_option"},
        ref=UUID("6fafda2c-6505-57a5-a088-25ea5d1d0364"),
    )
