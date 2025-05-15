from datetime import datetime
from typing import Any, Callable, Dict, Optional, cast
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
from pybotx.models.enums import ConferenceLinkTypes
from pybotx.models.system_events.conference_changed import ConferenceChangedEvent
from tests.system_events.factories import ConferenceChangedDataFactory

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__conference_changed_succeed(
    bot_account: BotAccountWithSecret,
    datetime_formatter: Callable[[str], datetime],
    bot_id: UUID,
    call_id: UUID,
    host: str,
    api_incoming_message_factory: Callable[..., Dict[str, Any]],
) -> None:
    # - Arrange -
    conference_change_data = cast(
        Dict[str, Any],
        ConferenceChangedDataFactory(
            call_id=str(call_id),
            link_type="public",
        ),  # type: ignore[no-untyped-call]
    )
    payload = api_incoming_message_factory(
        body="system:conference_changed",
        command_type="system",
        data=conference_change_data,
        bot_id=bot_id,
        host=host,
    )

    collector = HandlerCollector()
    conference_changed: Optional[ConferenceChangedEvent] = None

    @collector.conference_changed
    async def conference_changed_handler(
        event: ConferenceChangedEvent,
        bot: Bot,
    ) -> None:
        nonlocal conference_changed
        conference_changed = event

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    diff = DeepDiff(
        conference_changed,
        ConferenceChangedEvent(
            bot=BotAccount(id=bot_id, host=host),
            raw_command=payload,
            access_code=conference_change_data["access_code"],
            actor=conference_change_data["access_code"],
            added_users=list(map(UUID, conference_change_data["added_users"])),
            admins=list(map(UUID, conference_change_data["admins"])),
            call_id=call_id,
            deleted_users=list(map(UUID, conference_change_data["deleted_users"])),
            end_at=datetime_formatter(conference_change_data["end_at"]),
            link=conference_change_data["link"],
            link_id=UUID(conference_change_data["link_id"]),
            link_type=ConferenceLinkTypes.PUBLIC,
            members=list(map(UUID, conference_change_data["members"])),
            name=conference_change_data["name"],
            operation=conference_change_data["operation"],
            sip_number=conference_change_data["sip_number"],
            start_at=datetime_formatter(conference_change_data["start_at"]),
        ),
    )

    assert diff == {}, diff
