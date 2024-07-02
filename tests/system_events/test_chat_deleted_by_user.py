from typing import Optional
from uuid import UUID

import pytest

from pybotx import (
    Bot,
    BotAccount,
    BotAccountWithSecret,
    HandlerCollector,
    lifespan_wrapper,
)
from pybotx.models.system_events.chat_deleted_by_user import ChatDeletedByUserEvent

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__chat_deleted_by_user__succeed(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    payload = {
        "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
        "command": {
            "body": "system:chat_deleted_by_user",
            "data": {
                "group_chat_id": "6fa5f1e9-1453-0ad7-2d6d-b791467e382a",
                "user_huid": "37b821f5-a2be-5dc1-b107-87807ce97e56",
            },
            "command_type": "system",
            "metadata": {},
        },
        "async_files": [],
        "attachments": [],
        "entities": [],
        "from": {
            "user_huid": None,
            "group_chat_id": "6fa5f1e9-1453-0ad7-2d6d-b791467e382a",
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
    chat_deleted: Optional[ChatDeletedByUserEvent] = None

    @collector.chat_deleted_by_user
    async def chat_deleted_handler(event: ChatDeletedByUserEvent, bot: Bot) -> None:
        nonlocal chat_deleted
        chat_deleted = event
        # Drop `raw_command` from asserting
        chat_deleted.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    assert chat_deleted == ChatDeletedByUserEvent(
        sync_id=UUID("a465f0f3-1354-491c-8f11-f400164295cb"),
        bot=BotAccount(
            id=UUID("24348246-6791-4ac0-9d86-b948cd6a0e46"),
            host="cts.example.com",
        ),
        chat_id=UUID("6fa5f1e9-1453-0ad7-2d6d-b791467e382a"),
        huid=UUID("37b821f5-a2be-5dc1-b107-87807ce97e56"),
        raw_command=None,
    )
