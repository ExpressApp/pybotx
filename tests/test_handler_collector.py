import asyncio
from copy import deepcopy
from typing import Any
from collections.abc import Callable
from unittest.mock import Mock

import pytest

from pybotx import (
    Bot,
    BotAccountWithSecret,
    BotCommandOverloadAction,
    BotCommandProcessingConfig,
    BotCommandRejectedError,
    ChatCreatedEvent,
    DropOldestBotCommandOverloadStrategy,
    HandlerCollector,
    IncomingMessage,
    RejectNewBotCommandOverloadStrategy,
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
async def test__handler_collector__limits_incoming_commands_parallelism(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    started = 0
    running = 0
    max_running = 0
    started_event = asyncio.Event()
    release_event = asyncio.Event()
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        nonlocal started, running, max_running
        running += 1
        started += 1
        max_running = max(max_running, running)
        if started >= 2:
            started_event.set()
        await release_event.wait()
        running -= 1

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        command_processing_config=BotCommandProcessingConfig(
            max_concurrency=2,
            max_queue_size=10,
        ),
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        tasks = [
            bot.async_execute_bot_command(
                incoming_message_factory(body=f"/command {index}"),
            )
            for index in range(5)
        ]
        await asyncio.wait_for(started_event.wait(), timeout=1.0)
        await asyncio.sleep(0.05)
        release_event.set()
        await asyncio.gather(*tasks)

    # - Assert -
    assert max_running == 2


@pytest.mark.asyncio
async def test__handler_collector__reject_new_policy_when_queue_full(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    handled_messages: list[str] = []
    first_started_event = asyncio.Event()
    release_event = asyncio.Event()
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        handled_messages.append(message.body)
        if message.body.endswith("1"):
            first_started_event.set()
            await release_event.wait()

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        command_processing_config=BotCommandProcessingConfig(
            max_concurrency=1,
            max_queue_size=1,
            overload_strategy=RejectNewBotCommandOverloadStrategy(),
        ),
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task_1 = bot.async_execute_bot_command(incoming_message_factory(body="/command 1"))
        await asyncio.wait_for(first_started_event.wait(), timeout=1.0)
        task_2 = bot.async_execute_bot_command(incoming_message_factory(body="/command 2"))
        task_3 = bot.async_execute_bot_command(incoming_message_factory(body="/command 3"))

        with pytest.raises(BotCommandRejectedError, match="queue_overflow_reject_new"):
            await task_3

        release_event.set()
        await asyncio.gather(task_1, task_2)

    # - Assert -
    assert handled_messages == ["/command 1", "/command 2"]


@pytest.mark.asyncio
async def test__handler_collector__supports_custom_overload_strategy(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    class _CustomStrategy:
        def __init__(self) -> None:
            self.invocations = 0

        def on_queue_overflow(
            self,
            *,
            queue_size: int,
            queue_max_size: int,
        ) -> BotCommandOverloadAction:
            self.invocations += 1
            assert queue_size == queue_max_size == 1
            return BotCommandOverloadAction.REJECT_NEW

    strategy = _CustomStrategy()
    first_started_event = asyncio.Event()
    release_event = asyncio.Event()
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        if message.body.endswith("1"):
            first_started_event.set()
            await release_event.wait()

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        command_processing_config=BotCommandProcessingConfig(
            max_concurrency=1,
            max_queue_size=1,
            overload_strategy=strategy,
        ),
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task_1 = bot.async_execute_bot_command(incoming_message_factory(body="/command 1"))
        await asyncio.wait_for(first_started_event.wait(), timeout=1.0)
        bot.async_execute_bot_command(incoming_message_factory(body="/command 2"))
        task_3 = bot.async_execute_bot_command(incoming_message_factory(body="/command 3"))

        with pytest.raises(BotCommandRejectedError, match="queue_overflow_reject_new"):
            await task_3
        release_event.set()
        await task_1

    # - Assert -
    assert strategy.invocations == 1


@pytest.mark.asyncio
async def test__handler_collector__drop_oldest_policy_when_queue_full(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    handled_messages: list[str] = []
    first_started_event = asyncio.Event()
    release_event = asyncio.Event()
    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        handled_messages.append(message.body)
        if message.body.endswith("1"):
            first_started_event.set()
            await release_event.wait()

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        command_processing_config=BotCommandProcessingConfig(
            max_concurrency=1,
            max_queue_size=1,
            overload_strategy=DropOldestBotCommandOverloadStrategy(),
        ),
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        task_1 = bot.async_execute_bot_command(incoming_message_factory(body="/command 1"))
        await asyncio.wait_for(first_started_event.wait(), timeout=1.0)
        task_2 = bot.async_execute_bot_command(incoming_message_factory(body="/command 2"))
        task_3 = bot.async_execute_bot_command(incoming_message_factory(body="/command 3"))

        with pytest.raises(BotCommandRejectedError, match="queue_overflow_drop_oldest"):
            await task_2

        release_event.set()
        await asyncio.gather(task_1, task_3)

    # - Assert -
    assert handled_messages == ["/command 1", "/command 3"]


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
        ) -> Any: ...

    assert str(exc.value) == "Handler for sync smartapp event already registered"
