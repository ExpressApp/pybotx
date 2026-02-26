from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from pybotx import Bot, IncomingMessage

from pybotx.widgets.base import Widget
from pybotx.widgets.runner import (
    RunnerHookResult,
    WidgetRunner,
    on_action,
    on_completed,
    on_data_key,
    widget_command,
)


class _DummyWidget(Widget):
    def add_markup(self) -> None:
        self.widget_message.body = "dummy"


class _AltWidget(Widget):
    def add_markup(self) -> None:
        self.widget_message.body = "alt"


def _build_bot_mock() -> SimpleNamespace:
    return SimpleNamespace(
        send=AsyncMock(return_value=uuid4()),
        edit_message=AsyncMock(),
        answer_message=AsyncMock(return_value=uuid4()),
    )


@pytest.mark.asyncio
async def test__widget_runner__display_only(
    incoming_message_factory: object,
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
    incoming_message_factory: object,
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
    incoming_message_factory: object,
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
    incoming_message_factory: object,
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
    incoming_message_factory: object,
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
    incoming_message_factory: object,
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
    incoming_message_factory: object,
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
    incoming_message_factory: object,
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
    incoming_message_factory: object,
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
    incoming_message_factory: object,
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
    incoming_message_factory: object,
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
