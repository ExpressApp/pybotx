from datetime import datetime
from typing import Any
from collections.abc import Callable
from uuid import UUID

import pytest
from deepdiff import DeepDiff

from pybotx import (
    build_bot,
    Bot,
    BotAccount,
    BotAccountWithSecret,
    EventDeleted,
    HandlerCollector,
    lifespan_wrapper,
)
from pybotx.presentation.raw_handlers import async_execute_raw_bot_command

from tests.system_events.factories import DeleteEventFactory

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__event_delete__succeed(
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
    host: str,
    datetime_formatter: Callable[[str], datetime],
    api_incoming_message_factory: Callable[..., dict[str, Any]],
) -> None:
    # - Arrange -
    event_deleted_data = DeleteEventFactory.create()

    payload = api_incoming_message_factory(
        body="system:event_deleted",
        command_type="system",
        data=event_deleted_data,
        bot_id=bot_id,
        host=host,
    )

    collector = HandlerCollector()
    event_deleted: EventDeleted | None = None

    @collector.event_deleted
    async def event_deleted_handler(event: EventDeleted, _: Bot) -> None:
        nonlocal event_deleted
        event_deleted = event
        # Drop `raw_command` from asserting
        event_deleted.raw_command = None

    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        async_execute_raw_bot_command(bot, payload, verify_request=False)

    # - Assert -
    diff = DeepDiff(
        event_deleted,
        EventDeleted(
            bot=BotAccount(id=bot_id, host=host),
            raw_command=None,
            deleted_at=datetime_formatter(event_deleted_data["deleted_at"]),
            meta=event_deleted_data["meta"],
            group_chat_id=UUID(event_deleted_data["group_chat_id"]),
            sync_ids=[UUID(uuid_str) for uuid_str in event_deleted_data["sync_ids"]],
        ),
    )

    assert diff == {}, diff
