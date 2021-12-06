from typing import Callable
from unittest.mock import Mock

import pytest
import respx

from botx import (
    Bot,
    BotAccount,
    ChatCreatedEvent,
    HandlerCollector,
    HandlerNotFoundError,
    IncomingMessage,
    lifespan_wrapper,
)


@pytest.fixture
def collector() -> HandlerCollector:
    return HandlerCollector()


def test__handler_collector__command_with_space_error_raised(
    collector: HandlerCollector,
) -> None:
    # - Arrange -
    with pytest.raises(ValueError) as exc:

        @collector.command("/ command", description="My command")
        async def handler(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "include space" in str(exc.value)


def test__handler_collector__command_without_leading_slash_error_raised(
    collector: HandlerCollector,
) -> None:
    # - Arrange -
    with pytest.raises(ValueError) as exc:

        @collector.command("command", description="My command")
        async def handler(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "should start with '/'" in str(exc.value)


def test__handler_collector__visible_command_without_description_error_raised(
    collector: HandlerCollector,
) -> None:
    # - Act -
    with pytest.raises(ValueError) as exc:

        @collector.command("/command")
        async def handler(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "Description is required" in str(exc.value)


def test__handler_collector__two_same_commands_error_raised(
    collector: HandlerCollector,
) -> None:
    # - Arrange -
    @collector.command("/command", description="My command")
    async def handler_1(message: IncomingMessage, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:

        @collector.command("/command", description="My command")
        async def handler_2(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "already registered" in str(exc.value)
    assert "/command" in str(exc.value)


def test__handler_collector__two_default_handlers_error_raised(
    collector: HandlerCollector,
) -> None:
    # - Arrange -
    @collector.default_message_handler
    async def handler_1(message: IncomingMessage, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:

        @collector.default_message_handler
        async def handler_2(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "already registered" in str(exc.value)
    assert "Default" in str(exc.value)


def test__handler_collector__two_same_system_events_handlers_error_raised(
    collector: HandlerCollector,
) -> None:
    # - Arrange -
    @collector.chat_created
    async def handler_1(message: ChatCreatedEvent, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:

        @collector.chat_created
        async def handler_2(message: ChatCreatedEvent, bot: Bot) -> None:
            pass

    # - Assert -
    assert "already registered" in str(exc.value)
    assert "Event" in str(exc.value)


def test___handler_collector__merge_collectors_with_same_command_error_raised(
    collector: HandlerCollector,
) -> None:
    # - Arrange -
    @collector.command("/command", description="My command")
    async def handler_1(message: IncomingMessage, bot: Bot) -> None:
        pass

    other_collector = HandlerCollector()

    @other_collector.command("/command", description="My command")
    async def handler_2(message: IncomingMessage, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:
        collector.include(other_collector)

    # - Assert -
    assert "already registered" in str(exc.value)
    assert "/command" in str(exc.value)


def test__handler_collector__merge_collectors_with_default_handlers_error_raised(
    collector: HandlerCollector,
) -> None:
    # - Arrange -
    @collector.default_message_handler
    async def handler_1(message: IncomingMessage, bot: Bot) -> None:
        pass

    other_collector = HandlerCollector()

    @other_collector.default_message_handler
    async def handler_2(message: IncomingMessage, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:
        collector.include(other_collector)

    # - Assert -
    assert "already registered" in str(exc.value)
    assert "Default" in str(exc.value)


def test__handler_collector__merge_collectors_with_same_system_events_handlers_error_raised(
    collector: HandlerCollector,
) -> None:
    # - Arrange -
    @collector.chat_created
    async def handler_1(message: ChatCreatedEvent, bot: Bot) -> None:
        pass

    other_collector = HandlerCollector()

    @other_collector.chat_created
    async def handler_2(message: ChatCreatedEvent, bot: Bot) -> None:
        pass

    # - Act -
    with pytest.raises(ValueError) as exc:
        collector.include(other_collector)

    # - Assert -
    assert "already registered" in str(exc.value)
    assert "event" in str(exc.value)


@respx.mock
@pytest.mark.asyncio
@pytest.mark.mock_authorization
async def test__handler_collector__command_handler_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
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
@pytest.mark.mock_authorization
async def test__handler_collector__unicode_command_error_raised(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
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
@pytest.mark.mock_authorization
async def test__handler_collector__correct_command_handler_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    incorrect_handler_trigger: Mock,
    bot_account: BotAccount,
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
@pytest.mark.mock_authorization
async def test__handler_collector__correct_command_handler_called_in_merged_collectors(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    incorrect_handler_trigger: Mock,
    bot_account: BotAccount,
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
@pytest.mark.mock_authorization
async def test__handler_collector__default_handler_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
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
@pytest.mark.mock_authorization
async def test__handler_collector__empty_command_goes_to_default_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
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
@pytest.mark.mock_authorization
async def test__handler_collector__invalid_command_goes_to_default_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
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
@pytest.mark.mock_authorization
async def test__handler_collector__handler_not_found_error_raised(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccount,
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
@pytest.mark.mock_authorization
async def test__handler_collector__default_handler_in_first_collector_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
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
@pytest.mark.mock_authorization
async def test__handler_collector__default_handler_in_second_collector_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccount,
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
