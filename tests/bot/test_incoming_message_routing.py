from typing import Callable
from unittest.mock import Mock

import pytest

from botx import Bot, HandlerCollector, HandlerNotFoundException, IncomingMessage
from botx.testing import lifespan_wrapper


@pytest.mark.asyncio
async def test_user_command(
    incoming_message_factory: Callable[..., IncomingMessage],
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    @collector.handler(command="/command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_botx_command(user_command)

    # - Assert -
    right_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test_non_ascii_user_command(
    incoming_message_factory: Callable[..., IncomingMessage],
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    russian_command = incoming_message_factory(body="/команда")
    collector = HandlerCollector()

    @collector.handler(command="/команда")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_botx_command(russian_command)

    # - Assert -
    right_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test_one_collector_and_two_handlers(
    incoming_message_factory: Callable[..., IncomingMessage],
    right_handler_trigger: Mock,
    wrong_handler_trigger: Mock,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    @collector.handler(command="/command-two")
    async def wrong_handler(message: IncomingMessage, bot: Bot) -> None:
        wrong_handler_trigger()

    @collector.handler(command="/command")
    async def right_handler(message: IncomingMessage, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_botx_command(user_command)

    # - Assert -
    right_handler_trigger.assert_called_once()
    wrong_handler_trigger.assert_not_called()


@pytest.mark.asyncio
async def test_two_collectors_and_commands(
    incoming_message_factory: Callable[..., IncomingMessage],
    right_handler_trigger: Mock,
    wrong_handler_trigger: Mock,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")

    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_1.handler(command="/command")
    async def right_handler(message: IncomingMessage, bot: Bot) -> None:
        right_handler_trigger()

    @collector_2.handler(command="/command-two")
    async def wrong_handler(message: IncomingMessage, bot: Bot) -> None:
        wrong_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_botx_command(user_command)

    # - Assert -
    right_handler_trigger.assert_called_once()
    wrong_handler_trigger.assert_not_called()


@pytest.mark.asyncio
async def test_default_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    @collector.default
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_botx_command(user_command)

    # - Assert -
    right_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test_empty_command_goes_to_default_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    empty_command = incoming_message_factory(body="")
    collector = HandlerCollector()

    @collector.default
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_botx_command(empty_command)

    # - Assert -
    right_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test_invalid_command_goes_to_default_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    empty_command = incoming_message_factory(body="/")
    collector = HandlerCollector()

    @collector.default
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_botx_command(empty_command)

    # - Assert -
    right_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test_unknown_command_and_no_default_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    built_bot = Bot(collectors=[collector])

    # - Act -
    # Exception throws in background task so we need to wrap lifespan
    with pytest.raises(HandlerNotFoundException) as exc:
        async with lifespan_wrapper(built_bot) as bot:
            bot.async_execute_botx_command(user_command)

    # - Assert -
    assert "/command" in str(exc)


@pytest.mark.asyncio
async def test_default_handler_in_first_collector(
    incoming_message_factory: Callable[..., IncomingMessage],
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")

    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_1.default
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_botx_command(user_command)

    # - Assert -
    right_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test_default_handler_in_second_collector(
    incoming_message_factory: Callable[..., IncomingMessage],
    right_handler_trigger: Mock,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")

    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_2.default
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        right_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_botx_command(user_command)

    # - Assert -
    right_handler_trigger.assert_called_once()
