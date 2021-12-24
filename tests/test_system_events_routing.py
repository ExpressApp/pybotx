from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    BotAccountWithSecret,
    Chat,
    ChatCreatedEvent,
    ChatCreatedMember,
    ChatTypes,
    HandlerCollector,
    UserKinds,
    lifespan_wrapper,
)


@pytest.fixture
def chat_created(
    bot_id: UUID,
) -> ChatCreatedEvent:
    return ChatCreatedEvent(
        bot=BotAccount(
            id=bot_id,
            host="cts.example.com",
        ),
        sync_id=uuid4(),
        chat_name="Test",
        chat=Chat(
            id=uuid4(),
            type=ChatTypes.PERSONAL_CHAT,
        ),
        creator_id=uuid4(),
        members=[
            ChatCreatedMember(
                is_admin=False,
                huid=uuid4(),
                username="Ivanov Ivan Ivanovich",
                kind=UserKinds.CTS_USER,
            ),
        ],
        raw_command=None,
    )


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__system_event_handler__called(
    chat_created: ChatCreatedEvent,
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    correct_handler_trigger.assert_called_once()


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__system_event_handler__no_handler_for_system_event(
    chat_created: ChatCreatedEvent,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    # This test is considered as passed if no exception was raised


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__system_event_handler__handler_in_first_collector(
    chat_created: ChatCreatedEvent,
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_1.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    correct_handler_trigger.assert_called_once()


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__system_event_handler__handler_in_second_collector(
    chat_created: ChatCreatedEvent,
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_2.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    correct_handler_trigger.assert_called_once()
