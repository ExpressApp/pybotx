from collections.abc import Callable
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4
from typing import Any

import pytest
from pybotx import Bot, IncomingMessage

from pybotx.widgets.base import Widget
from pybotx.widgets.runner import (
    LoggingWidgetRunnerObserver,
    RunnerHookResult,
    WidgetRunner,
    WidgetRunnerConfig,
    WidgetRunnerFinishedEvent,
    WidgetRunnerObserver,
    WidgetRunnerStartedEvent,
    on_action,
    on_completed,
    on_data_key,
    widget_command,
    _resolve_awaitable,
)


class _DummyWidget(Widget):
    def add_markup(self) -> None:
        self.widget_message.body = "dummy"


class _AltWidget(Widget):
    def add_markup(self) -> None:
        self.widget_message.body = "alt"


class _FailingWidget(Widget):
    def add_markup(self) -> None:
        raise RuntimeError("Widget rendering failed.")


class _RecordingObserver(WidgetRunnerObserver):
    def __init__(self) -> None:
        self.started: list[WidgetRunnerStartedEvent] = []
        self.finished: list[WidgetRunnerFinishedEvent] = []

    async def on_started(self, event: WidgetRunnerStartedEvent) -> None:
        self.started.append(event)

    async def on_finished(self, event: WidgetRunnerFinishedEvent) -> None:
        self.finished.append(event)


def _build_bot_mock() -> Any:
    return SimpleNamespace(
        send=AsyncMock(return_value=uuid4()),
        edit_message=AsyncMock(),
        answer_message=AsyncMock(return_value=uuid4()),
    )


@pytest.mark.asyncio
async def test__widget_runner__display_only(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    runner = WidgetRunner(message, bot)
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    await runner.run(widget=widget)

    assert bot.send.await_count == 1
    assert bot.send.await_args.kwargs["message"].body == "dummy"


@pytest.mark.asyncio
async def test__widget_runner__before_result_skip_display(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    runner = WidgetRunner(message, bot)
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    def _before(_: _DummyWidget) -> RunnerHookResult:
        return RunnerHookResult(result="before", should_display=False)

    await runner.run(widget=widget, before=_before)

    assert bot.send.await_count == 1
    assert bot.send.await_args.kwargs["message"].body == "before"


@pytest.mark.asyncio
async def test__widget_runner__before_result_and_display(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    runner = WidgetRunner(message, bot)
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    def _before(_: _DummyWidget) -> RunnerHookResult:
        return RunnerHookResult(result="before", should_display=True)

    await runner.run(widget=widget, before=_before)

    assert bot.send.await_count == 2
    assert bot.send.await_args_list[0].kwargs["message"].body == "before"
    assert bot.send.await_args_list[1].kwargs["message"].body == "dummy"


@pytest.mark.asyncio
async def test__widget_runner__before_replace_widget(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    runner = WidgetRunner(message, bot)
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")
    replacement = _AltWidget(message=message, bot=bot, command="/alt")

    def _before(_: _DummyWidget) -> RunnerHookResult:
        return RunnerHookResult(widget=replacement)

    await runner.run(widget=widget, before=_before)

    assert bot.send.await_count == 1
    assert bot.send.await_args.kwargs["message"].body == "alt"


@pytest.mark.asyncio
async def test__widget_runner__after_async_result(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    runner = WidgetRunner(message, bot)
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    async def _after(_: _DummyWidget) -> str | None:
        return "after"

    await runner.run(widget=widget, after=_after)

    assert bot.send.await_count == 2
    assert bot.send.await_args_list[0].kwargs["message"].body == "dummy"
    assert bot.send.await_args_list[1].kwargs["message"].body == "after"


@pytest.mark.asyncio
async def test__widget_runner__on_data_key_skip_display(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    message.data["select"] = "value"
    bot = _build_bot_mock()

    runner = WidgetRunner(message, bot)
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    await runner.run(
        widget=widget,
        before=on_data_key("select", lambda _: "selected"),
    )

    assert bot.send.await_count == 1
    assert bot.send.await_args.kwargs["message"].body == "selected"


@pytest.mark.asyncio
async def test__widget_runner__on_data_key_keep_display(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    message.data["select"] = "value"
    bot = _build_bot_mock()

    runner = WidgetRunner(message, bot)
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    await runner.run(
        widget=widget,
        before=on_data_key(
            "select",
            lambda _: "selected",
            should_display=True,
        ),
    )

    assert bot.send.await_count == 2
    assert bot.send.await_args_list[0].kwargs["message"].body == "selected"
    assert bot.send.await_args_list[1].kwargs["message"].body == "dummy"


@pytest.mark.asyncio
async def test__widget_runner__on_completed_after(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    runner = WidgetRunner(message, bot)
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    await runner.run(
        widget=widget,
        after=on_completed(lambda _: True, lambda _: "completed"),
    )

    assert bot.send.await_count == 2
    assert bot.send.await_args_list[0].kwargs["message"].body == "dummy"
    assert bot.send.await_args_list[1].kwargs["message"].body == "completed"


@pytest.mark.asyncio
async def test__widget_runner__on_action_map(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    message.data["action"] = "confirm"
    bot = _build_bot_mock()

    runner = WidgetRunner(message, bot)
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    await runner.run(
        widget=widget,
        before=on_action(
            lambda current_widget: str(current_widget.message.data["action"]),
            {"confirm": "confirmed"},
        ),
    )

    assert bot.send.await_count == 1
    assert bot.send.await_args.kwargs["message"].body == "confirmed"


@pytest.mark.asyncio
async def test__widget_runner__on_action_missing_value_is_ignored(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    runner = WidgetRunner(message, bot)
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    def _getter(current_widget: _DummyWidget) -> str:
        action = current_widget.message.data.get("action")
        if action is None:
            raise RuntimeError("Action is missing.")
        return str(action)

    await runner.run(
        widget=widget,
        before=on_action(_getter, {"confirm": "confirmed"}),
    )

    assert bot.send.await_count == 1
    assert bot.send.await_args.kwargs["message"].body == "dummy"


@pytest.mark.asyncio
async def test__widget_runner__widget_command_decorator(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    message.data["selected"] = "1"
    bot = _build_bot_mock()

    @widget_command(
        before=on_data_key(
            "selected",
            lambda _: "handled by decorator",
        ),
    )
    async def _handler(
        wrapped_message: IncomingMessage,
        wrapped_bot: Bot,
    ) -> _DummyWidget:
        return _DummyWidget(
            message=wrapped_message,
            bot=wrapped_bot,
            command="/dummy",
        )

    await _handler(message, bot)

    assert bot.send.await_count == 1
    assert bot.send.await_args.kwargs["message"].body == "handled by decorator"


@pytest.mark.asyncio
async def test__widget_runner__config_before_runs_before_call_before(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    calls: list[str] = []

    def _config_before(_: _DummyWidget) -> RunnerHookResult:
        calls.append("config_before")
        return RunnerHookResult(result="config", should_display=True)

    def _call_before(_: _DummyWidget) -> RunnerHookResult:
        calls.append("call_before")
        return RunnerHookResult(result="call", should_display=True)

    runner = WidgetRunner(
        message,
        bot,
        config=WidgetRunnerConfig.from_hooks(before=_config_before),
    )
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    await runner.run(widget=widget, before=_call_before)

    assert calls == ["config_before", "call_before"]
    assert bot.send.await_count == 3
    assert bot.send.await_args_list[0].kwargs["message"].body == "config"
    assert bot.send.await_args_list[1].kwargs["message"].body == "call"
    assert bot.send.await_args_list[2].kwargs["message"].body == "dummy"


@pytest.mark.asyncio
async def test__widget_runner__config_after_runs_after_call_after(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    calls: list[str] = []

    def _call_after(_: _DummyWidget) -> str | None:
        calls.append("call_after")
        return "call"

    def _config_after(_: _DummyWidget) -> str | None:
        calls.append("config_after")
        return "config"

    runner = WidgetRunner(
        message,
        bot,
        config=WidgetRunnerConfig.from_hooks(after=_config_after),
    )
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    await runner.run(widget=widget, after=_call_after)

    assert calls == ["call_after", "config_after"]
    assert bot.send.await_count == 3
    assert bot.send.await_args_list[0].kwargs["message"].body == "dummy"
    assert bot.send.await_args_list[1].kwargs["message"].body == "call"
    assert bot.send.await_args_list[2].kwargs["message"].body == "config"


@pytest.mark.asyncio
async def test__widget_runner__observer_receives_started_and_finished_events(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    observer = _RecordingObserver()

    runner = WidgetRunner(
        message,
        bot,
        config=WidgetRunnerConfig(observers=(observer, LoggingWidgetRunnerObserver())),
    )
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    await runner.run(widget=widget)

    assert len(observer.started) == 1
    assert observer.started[0].widget_name == "_DummyWidget"
    assert len(observer.finished) == 1
    assert observer.finished[0].widget_name == "_DummyWidget"
    assert observer.finished[0].displayed is True
    assert observer.finished[0].error is None
    assert observer.finished[0].before_results_sent == 0
    assert observer.finished[0].after_results_sent == 0


@pytest.mark.asyncio
async def test__widget_runner__observer_errors_do_not_break_execution(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    class _BrokenObserver(WidgetRunnerObserver):
        async def on_started(self, event: WidgetRunnerStartedEvent) -> None:
            raise RuntimeError("start failed")

        async def on_finished(self, event: WidgetRunnerFinishedEvent) -> None:
            raise RuntimeError("finish failed")

    runner = WidgetRunner(
        message,
        bot,
        config=WidgetRunnerConfig(observers=(_BrokenObserver(),)),
    )
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    await runner.run(widget=widget)

    assert bot.send.await_count == 1
    assert bot.send.await_args.kwargs["message"].body == "dummy"


@pytest.mark.asyncio
async def test__widget_runner__observer_receives_error_event(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    observer = _RecordingObserver()

    runner = WidgetRunner(
        message,
        bot,
        config=WidgetRunnerConfig(observers=(observer,)),
    )
    widget = _FailingWidget(message=message, bot=bot, command="/dummy")

    with pytest.raises(RuntimeError, match="Widget rendering failed"):
        await runner.run(widget=widget)

    assert len(observer.started) == 1
    assert len(observer.finished) == 1
    assert observer.finished[0].displayed is False
    assert observer.finished[0].error is not None
    assert str(observer.finished[0].error) == "Widget rendering failed."


@pytest.mark.asyncio
async def test__widget_runner__widget_command_supports_config(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    def _config_before(_: _DummyWidget) -> RunnerHookResult:
        return RunnerHookResult(result="configured", should_display=False)

    config = WidgetRunnerConfig.from_hooks(before=_config_before)

    @widget_command(config=config)
    async def _handler(
        wrapped_message: IncomingMessage,
        wrapped_bot: Bot,
    ) -> _DummyWidget:
        return _DummyWidget(
            message=wrapped_message,
            bot=wrapped_bot,
            command="/dummy",
        )

    await _handler(message, bot)

    assert bot.send.await_count == 1
    assert bot.send.await_args.kwargs["message"].body == "configured"


@pytest.mark.asyncio
async def test__widget_runner__edge_paths(
    incoming_message_factory: Callable[[], IncomingMessage],
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")
    started = WidgetRunnerStartedEvent(message=message, bot=bot, widget=widget)
    finished = WidgetRunnerFinishedEvent(
        message=message,
        bot=bot,
        initial_widget=widget,
        widget=widget,
        duration_seconds=0,
        displayed=False,
        skipped_by_before=False,
        before_results_sent=0,
        after_results_sent=0,
        error=RuntimeError("failed"),
    )
    observer = WidgetRunnerObserver()

    assert started.result_mode == widget.result_mode
    assert observer.on_started(started) is None
    assert observer.on_finished(finished) is None
    await LoggingWidgetRunnerObserver(log_start=True).on_started(started)
    await LoggingWidgetRunnerObserver().on_finished(finished)

    runner = WidgetRunner(
        message,
        bot,
        config=WidgetRunnerConfig(after_hooks=(lambda _widget: None,)),
    )
    await runner.run(widget=widget)

    @widget_command
    def direct_handler(_message: IncomingMessage, _bot: Bot) -> None:
        return None

    await direct_handler(message, bot)
    assert await _resolve_awaitable(
        on_data_key("missing", lambda _: "unused")(widget),
    ) is None
    assert await _resolve_awaitable(
        on_completed(lambda _: False, lambda _: "unused")(widget),
    ) is None
    assert await _resolve_awaitable(on_action(lambda _: "missing", {})(widget)) is None
    assert await _resolve_awaitable(
        on_action(lambda _: "run", {"run": lambda _: "done"})(widget),
    ) == (
        RunnerHookResult(result="done", should_display=False)
    )
    assert await _resolve_awaitable(
        on_action(
            lambda _: "run",
            {"run": RunnerHookResult(result="ready")},
        )(widget),
    ) == RunnerHookResult(result="ready")
