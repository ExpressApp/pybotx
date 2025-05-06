from typing import Any, Optional
from uuid import UUID

import pytest

from pybotx import (
    Bot,
    BotAccount,
    BotAccountWithSecret,
    Chat,
    ChatTypes,
    HandlerCollector,
    lifespan_wrapper,
)
from pybotx.models.system_events.user_joined_to_chat import JoinToChatEvent
from tests.system_events.factories import BotAPIJoinToChatFactory  # type: ignore

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__join_to_chat__succeed(
    bot_account: BotAccountWithSecret,
) -> None:
    """Verifies  user joining chat message processing.

    The test checks that:
    1. The system:user_joined_to_chat event is properly routed
    2. The event data is correctly converted to a UserJoinedToChatEvent object
    3. The registered user_joined_to_chat handler is called with this event
    """

    payload: dict[str, Any] = BotAPIJoinToChatFactory(bot_id=bot_account.id.hex)

    collector = HandlerCollector()
    join_to_chat: Optional[JoinToChatEvent] = None

    @collector.user_joined_to_chat
    async def join_to_chat_handler(event: JoinToChatEvent, bot: Bot) -> None:
        nonlocal join_to_chat
        join_to_chat = event
        # Drop `raw_command` from asserting
        join_to_chat.raw_command = None

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_raw_bot_command(payload, verify_request=False)

    # - Assert -
    expected_event = JoinToChatEvent(
        bot=BotAccount(
            id=bot_account.id,
            host=payload["from"]["host"],
        ),
        raw_command=None,
        huids=list(map(UUID, payload["command"]["data"]["added_members"])),
        chat=Chat(
            id=UUID(payload["from"]["group_chat_id"]),
            type=ChatTypes.GROUP_CHAT,
        ),
    )

    assert join_to_chat == expected_event
