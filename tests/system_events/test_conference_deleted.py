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
    HandlerCollector,
    lifespan_wrapper,
)
from pybotx.presentation.raw_handlers import async_execute_raw_bot_command

from pybotx.domain.models.system_events.conference_deleted import ConferenceDeletedEvent

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__conference_deleted_succeed(
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
    host: str,
    call_id: UUID,
    api_incoming_message_factory: Callable[..., dict[str, Any]],
) -> None:
    # - Arrange -
    payload = api_incoming_message_factory(
        body="system:conference_deleted",
        command_type="system",
        data={"call_id": str(call_id)},
        bot_id=bot_id,
        host=host,
    )

    collector = HandlerCollector()
    conference_deleted: ConferenceDeletedEvent | None = None

    @collector.conference_deleted
    async def conference_deleted_handler(
        event: ConferenceDeletedEvent,
        bot: Bot,
    ) -> None:
        nonlocal conference_deleted
        conference_deleted = event

    built_bot = build_bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        async_execute_raw_bot_command(bot, payload, verify_request=False)

    # - Assert -
    diff = DeepDiff(
        conference_deleted,
        ConferenceDeletedEvent(
            bot=BotAccount(id=bot_id, host=host),
            raw_command=payload,
            call_id=call_id,
        ),
    )

    assert diff == {}, diff
