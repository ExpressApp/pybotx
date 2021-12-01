from typing import Callable
from unittest.mock import Mock

import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    HandlerCollector,
    HandlerNotFoundError,
    IncomingMessage,
    lifespan_wrapper,
)


@respx.mock
@pytest.mark.asyncio
async def test__handler_collector__command_handler_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    correct_handler_trigger.assert_called_once()


@respx.mock
@pytest.mark.asyncio
async def test__handler_collector__unicode_command_error_raised(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    russian_command = incoming_message_factory(body="/команда")
    collector = HandlerCollector()

    @collector.command("/команда", description="Моя команда")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(russian_command)

    # - Assert -
    correct_handler_trigger.assert_called_once()


@respx.mock
@pytest.mark.asyncio
async def test__handler_collector__correct_command_handler_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    incorrect_handler_trigger: Mock,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def correct_handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    @collector.command("/other", description="My command")
    async def incorrect_handler(message: IncomingMessage, bot: Bot) -> None:
        incorrect_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    correct_handler_trigger.assert_called_once()
    incorrect_handler_trigger.assert_not_called()


@respx.mock
@pytest.mark.asyncio
async def test__handler_collector__correct_command_handler_called_in_merged_collectors(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    incorrect_handler_trigger: Mock,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")

    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_1.command("/command", description="My command")
    async def correct_handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    @collector_2.command("/command-two", description="My command")
    async def incorrect_handler(message: IncomingMessage, bot: Bot) -> None:
        incorrect_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    correct_handler_trigger.assert_called_once()
    incorrect_handler_trigger.assert_not_called()


@respx.mock
@pytest.mark.asyncio
async def test__handler_collector__default_handler_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    @collector.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    correct_handler_trigger.assert_called_once()


@respx.mock
@pytest.mark.asyncio
async def test__handler_collector__empty_command_goes_to_default_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    empty_command = incoming_message_factory(body="")
    collector = HandlerCollector()

    @collector.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(empty_command)

    # - Assert -
    correct_handler_trigger.assert_called_once()


@respx.mock
@pytest.mark.asyncio
async def test__handler_collector__invalid_command_goes_to_default_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    empty_command = incoming_message_factory(body="/")
    collector = HandlerCollector()

    @collector.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(empty_command)

    # - Assert -
    correct_handler_trigger.assert_called_once()


@respx.mock
@pytest.mark.asyncio
async def test__handler_collector__handler_not_found_error_raised(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    # Exception throws in background task so we need to wrap lifespan
    with pytest.raises(HandlerNotFoundError) as exc:
        async with lifespan_wrapper(built_bot) as bot:
            bot.async_execute_bot_command(user_command)

    # - Assert -
    assert "/command" in str(exc.value)


@respx.mock
@pytest.mark.asyncio
async def test__handler_collector__default_handler_in_first_collector_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")

    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_1.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    correct_handler_trigger.assert_called_once()


@respx.mock
@pytest.mark.asyncio
async def test__handler_collector__default_handler_in_second_collector_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
    mock_authorization: None,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")

    collector_1 = HandlerCollector()
    collector_2 = HandlerCollector()

    @collector_2.default_message_handler
    async def default_handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector_1, collector_2], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    correct_handler_trigger.assert_called_once()
