from unittest.mock import Mock

import pytest

from botx import Bot, ChatCreatedEvent, HandlerCollector, lifespan_wrapper


@pytest.mark.asyncio
async def test_system_event_handling(
    chat_created: ChatCreatedEvent,
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    right_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test_no_handler_for_system_event(
    chat_created: ChatCreatedEvent,
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    # This test is considered as passed if no exception was raised


@pytest.mark.asyncio
async def test_system_event_in_first_collector(
    chat_created: ChatCreatedEvent,
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_1.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    right_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test_system_event_in_second_collector(
    chat_created: ChatCreatedEvent,
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_2.chat_created
    async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(chat_created)

    # - Assert -
    right_handler_trigger.assert_called_once()
