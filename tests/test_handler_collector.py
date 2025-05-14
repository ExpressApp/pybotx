from copy import deepcopy
from typing import Any, Callable
from unittest.mock import Mock

import pytest

from pybotx import (
    Bot,
    BotAccountWithSecret,
    ChatCreatedEvent,
    HandlerCollector,
    IncomingMessage,
    SmartAppEvent,
    SyncSmartAppEventHandlerNotFoundError,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


def test__handler_collector__command_with_space_error_raised() -> None:
    # - Arrange -
    collector = HandlerCollector()

    with pytest.raises(ValueError) as exc:

        @collector.command("/ command", description="My command")
        async def handler(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "include space" in str(exc.value)


def test__handler_collector__command_without_leading_slash_error_raised() -> None:
    # - Arrange -
    collector = HandlerCollector()

    with pytest.raises(ValueError) as exc:

        @collector.command("command", description="My command")
        async def handler(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "should start with '/'" in str(exc.value)


def test__handler_collector__visible_command_without_description_error_raised() -> None:
    # - Act -
    collector = HandlerCollector()

    with pytest.raises(ValueError) as exc:

        @collector.command("/command")
        async def handler(message: IncomingMessage, bot: Bot) -> None:
            pass

    # - Assert -
    assert "Description is required" in str(exc.value)


def test__handler_collector__two_same_commands_error_raised() -> None:
    # - Arrange -
    collector = HandlerCollector()

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


def test__handler_collector__two_default_handlers_error_raised() -> None:
    # - Arrange -
    collector = HandlerCollector()

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


def test__handler_collector__two_same_system_events_handlers_error_raised() -> None:
    # - Arrange -
    collector = HandlerCollector()

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


def test___handler_collector__merge_collectors_with_same_command_error_raised() -> None:
    # - Arrange -
    collector = HandlerCollector()

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


def test__handler_collector__merge_collectors_with_default_handlers_error_raised() -> (
    None
):
    # - Arrange -
    collector = HandlerCollector()

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


def test__handler_collector__merge_collectors_with_same_system_events_handlers_error_raised() -> (
    None
):
    # - Arrange -
    collector = HandlerCollector()

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


@pytest.mark.asyncio
async def test__handler_collector__command_handler_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
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


@pytest.mark.asyncio
async def test__handler_collector__unicode_command_error_raised(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
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


@pytest.mark.asyncio
async def test__handler_collector__correct_command_handler_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    incorrect_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
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


@pytest.mark.asyncio
async def test__handler_collector__correct_command_handler_called_in_merged_collectors(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    incorrect_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
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


@pytest.mark.asyncio
async def test__handler_collector__default_handler_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
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


@pytest.mark.asyncio
async def test__handler_collector__empty_command_goes_to_default_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
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


@pytest.mark.asyncio
async def test__handler_collector__invalid_command_goes_to_default_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
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


@pytest.mark.asyncio
async def test__handler_collector__handler_not_found_logged(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")
    collector = HandlerCollector()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert "`/command` not found" in loguru_caplog.text


@pytest.mark.asyncio
async def test__handler_collector__default_handler_in_first_collector_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
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


@pytest.mark.asyncio
async def test__handler_collector__default_handler_in_second_collector_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    correct_handler_trigger: Mock,
    bot_account: BotAccountWithSecret,
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


@pytest.mark.asyncio
async def test__handler_collector__handler_not_found_exception_logged(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    bot.async_execute_bot_command(incoming_message_factory(body="/command"))
    await bot.shutdown()

    # - Assert -
    assert "`/command` not found" in loguru_caplog.text


@pytest.mark.asyncio
async def test__handler_collector__handle_incoming_message_by_command_handler_not_found_exception_logged(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await collector.handle_incoming_message_by_command(
            incoming_message_factory(body="Text"),
            bot,
            command="/command",
        )

    # - Assert -
    assert "`/command` not found" in loguru_caplog.text


@pytest.mark.asyncio
async def test__handler_collector__handle_incoming_message_by_command_succeed(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
    correct_handler_trigger: Mock,
) -> None:
    # - Arrange -
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        correct_handler_trigger()

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        await collector.handle_incoming_message_by_command(
            incoming_message_factory(body="Text"),
            bot,
            command="/command",
        )

    # - Assert -
    correct_handler_trigger.assert_called_once()


@pytest.mark.asyncio
async def test__handler_collector__handle_sync_smartapp_event__handler_not_found(
    bot_account: BotAccountWithSecret,
    smartapp_event: SmartAppEvent,
) -> None:
    # - Arrange -
    collector = HandlerCollector()
    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act and Assert -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(SyncSmartAppEventHandlerNotFoundError):
            await collector.handle_sync_smartapp_event(
                bot,
                smartapp_event=smartapp_event,
            )


@pytest.mark.asyncio
async def test__handler_collector__sync_smartapp_event__include__handler_already_registered(
    collector_with_sync_smartapp_event_handler: HandlerCollector,
) -> None:
    # - Arrange -
    collector1 = collector_with_sync_smartapp_event_handler
    collector2 = deepcopy(collector_with_sync_smartapp_event_handler)

    # - Act and Assert -
    with pytest.raises(ValueError) as exc:
        collector1.include(collector2)

    assert str(exc.value) == "Handler for sync smartapp event already registered"


@pytest.mark.asyncio
async def test__handler_collector__sync_smartapp_event__decorator__handler_already_registered(
    collector_with_sync_smartapp_event_handler: HandlerCollector,
) -> None:
    # - Arrange -
    collector = collector_with_sync_smartapp_event_handler

    # - Act and Assert -
    with pytest.raises(ValueError) as exc:

        @collector.sync_smartapp_event
        async def duplicated_handle_sync_smartapp_event(
            *_: Any,
        ) -> Any: ...  # noqa: E704

    assert str(exc.value) == "Handler for sync smartapp event already registered"
