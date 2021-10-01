from unittest.mock import Mock

import pytest

from botx import Bot, ChatCreatedEvent, HandlerCollector, lifespan_wrapper


@pytest.mark.asyncio
async def test__system_event_handler__called(
    chat_created: ChatCreatedEvent,
    correct_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    correct_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test__system_event_handler__no_handler_for_system_event(
    chat_created: ChatCreatedEvent,
    correct_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    built_bot = Bot(collectors=[collector], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    # This test is considered as passed if no exception was raised


@pytest.mark.asyncio
async def test__system_event_handler__handler_in_first_collector(
    chat_created: ChatCreatedEvent,
    correct_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_1.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    correct_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test__system_event_handler__handler_in_second_collector(
    chat_created: ChatCreatedEvent,
    correct_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_2.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2], bot_accounts=[])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    correct_handler_trigger.assert_called_once()
