from typing import Optional
from uuid import UUID

import pytest

from pybotx import (
    Bot,
    BotAccount,
    BotAccountWithSecret,
    BotSender,
    Chat,
    ChatTypes,
    HandlerCollector,
    InternalBotNotificationEvent,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__internal_bot_notification__succeed(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = {
        "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
        "command": {
            "body": "system:internal_bot_notification",
            "data": {
                "data": {
                    "message": "ping",
                },
                "opts": {
                    "internal_token": "KyKfLJD1zMjNSJ1cQ4+8Lz",
                },
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
    internal_bot_notification: Optional[InternalBotNotificationEvent] = None

    @collector.internal_bot_notification
    async def internal_bot_notification_handler(
        event: InternalBotNotificationEvent,
        bot: Bot,
    ) -> None:
        nonlocal internal_bot_notification
        internal_bot_notification = event
        # Drop `raw_command` from asserting
        internal_bot_notification.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert internal_bot_notification == InternalBotNotificationEvent(
        bot=BotAccount(
            id=UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
            host="cts.example.com",
        ),
        raw_command=None,
        data={"message": "ping"},
        opts={"internal_token": "KyKfLJD1zMjNSJ1cQ4+8Lz"},
        chat=Chat(
            id=UUID("8dada2c8-67a6-4434-9dec-570d244e78ee"),
            type=ChatTypes.GROUP_CHAT,
        ),
        sender=BotSender(
            huid=UUID("b9197d3a-d855-5d34-ba8a-eff3a975ab20"),
            is_chat_admin=False,
            is_chat_creator=False,
        ),
    )
