from typing import Any, Callable, Dict, Optional
from uuid import UUID

import pytest
from deepdiff import DeepDiff

from pybotx import (
    Bot,
    BotAccount,
    BotAccountWithSecret,
    HandlerCollector,
    lifespan_wrapper,
)
from pybotx.models.system_events.conference_created import ConferenceCreatedEvent

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__conference_created_succeed(
    bot_account: BotAccountWithSecret,
    bot_id: UUID,
    host: str,
    call_id: UUID,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
) -> None:
    # - Arrange -
    payload = api_incoming_message_factory(
        body="system:conference_created",
        command_type="system",
        data={"call_id": str(call_id)},
        bot_id=bot_id,
        host=host,
    )

    collector = HandlerCollector()
    conference_created: Optional[ConferenceCreatedEvent] = None

    @collector.conference_created
    async def conference_created_handler(
        event: ConferenceCreatedEvent,
        bot: Bot,
    ) -> None:
        nonlocal conference_created
        conference_created = event

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    diff = DeepDiff(
        conference_created,
        ConferenceCreatedEvent(
            bot=BotAccount(id=bot_id, host=host),
            raw_command=payload,
            call_id=call_id,
        ),
    )

    assert diff == {}, diff
