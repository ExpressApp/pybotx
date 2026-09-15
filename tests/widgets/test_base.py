from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.missing import Undefined
from pybotx.widgets.base import (
    PYBOTX_WIDGET_FLAG,
    PYBOTX_WIDGET_RESULT_MODE_KEY,
    WIDGET_RESULT_MODE_EDIT,
    WIDGET_RESULT_MODE_MESSAGE,
    Widget,
    _normalize_result_mode,
    _parse_result_mode_from_argument,
    outgoing_markup,
)
from pybotx.widgets.markup import MessageMarkup


class _DummyWidget(Widget):
    def add_markup(self) -> None:
        self.widget_message.body = "dummy"
        self.widget_bubbles.add_button(command=self.command, label="dummy")


def _build_bot_mock() -> Any:
    return SimpleNamespace(
        send=AsyncMock(return_value=uuid4()),
        edit_message=AsyncMock(),
        answer_message=AsyncMock(return_value=uuid4()),
    )


@pytest.mark.asyncio
async def test__widget__display_send_message(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = _DummyWidget(message=message, bot=bot, command="/dummy")
    await widget.display()

    assert bot.send.await_count == 1
    assert bot.edit_message.await_count == 0

    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.body == "dummy"
    assert sent_message.metadata[PYBOTX_WIDGET_FLAG] == 1


@pytest.mark.asyncio
async def test__widget__display_edit_message(
    incoming_message_factory: Any,
) -> None:
    source_sync_id = uuid4()
    message = incoming_message_factory()
    message.metadata[PYBOTX_WIDGET_FLAG] = 1
    message.source_sync_id = source_sync_id
    bot = _build_bot_mock()

    widget = _DummyWidget(message=message, bot=bot, command="/dummy")
    await widget.display()

    assert bot.send.await_count == 0
    assert bot.edit_message.await_count == 1
    assert bot.edit_message.await_args.kwargs["sync_id"] == source_sync_id


def test__widget__add_additional_markup_merge(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    additional_markup = MessageMarkup()
    additional_markup.add_bubble(command="/extra", label="Extra")
    additional_markup.add_keyboard(command="/extra", label="Extra keyboard")

    widget = _DummyWidget(
        message=message,
        bot=bot,
        command="/dummy",
        additional_markup=additional_markup,
    )
    widget.add_markup()
    widget.add_additional_markup()

    rows = [[button.label for button in row] for row in widget.widget_bubbles]
    keyboard_rows = [
        [button.label for button in row] for row in widget.widget_keyboard
    ]

    assert rows == [["dummy"], ["Extra"]]
    assert keyboard_rows == [["Extra keyboard"]]


def test__widget__build_widget_metadata_from_undefined(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.metadata = {"foo": "bar"}
    bot = _build_bot_mock()

    widget = _DummyWidget(message=message, bot=bot, command="/dummy")
    metadata = widget._build_widget_metadata(Undefined)

    assert metadata == {"foo": "bar", PYBOTX_WIDGET_FLAG: 1}


def test__widget__outgoing_markup_for_undefined(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")
    widget.widget_message.bubbles = Undefined
    widget.widget_message.keyboard = Undefined

    markup = outgoing_markup(widget.widget_message)

    assert list(markup.bubbles) == []
    assert list(markup.keyboard) == []
    assert list(widget.widget_keyboard) == []


def test__widget__widget_metadata_for_undefined(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    widget = _DummyWidget(message=message, bot=bot, command="/dummy")
    widget.widget_message.metadata = Undefined

    assert widget.widget_metadata == {}


@pytest.mark.asyncio
async def test__widget__send_result_edit_mode(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.metadata = {PYBOTX_WIDGET_FLAG: 1}
    message.source_sync_id = uuid4()
    bot = _build_bot_mock()

    widget = _DummyWidget(message=message, bot=bot, command="/dummy")
    await widget.send_result("result")

    assert bot.edit_message.await_count == 1
    assert bot.send.await_count == 0


@pytest.mark.asyncio
async def test__widget__send_result_message_mode(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory(body="/dummy mode=message")
    message.metadata = {PYBOTX_WIDGET_FLAG: 1}
    message.source_sync_id = uuid4()
    bot = _build_bot_mock()

    widget = _DummyWidget(message=message, bot=bot, command="/dummy")
    await widget.send_result("result")

    assert bot.send.await_count == 0
    assert bot.edit_message.await_count == 0
    assert bot.answer_message.await_count == 1


def test__widget__result_mode_resolved_from_metadata(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.metadata = {PYBOTX_WIDGET_RESULT_MODE_KEY: WIDGET_RESULT_MODE_MESSAGE}
    bot = _build_bot_mock()

    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    assert widget.result_mode == WIDGET_RESULT_MODE_MESSAGE
    assert widget.widget_metadata[PYBOTX_WIDGET_RESULT_MODE_KEY] == WIDGET_RESULT_MODE_MESSAGE


def test__widget__result_mode_default(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = _DummyWidget(message=message, bot=bot, command="/dummy")

    assert widget.result_mode == WIDGET_RESULT_MODE_EDIT


def test__widget__result_mode_explicit_param_wins(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory(body="/dummy mode=edit")
    message.metadata = {PYBOTX_WIDGET_RESULT_MODE_KEY: WIDGET_RESULT_MODE_EDIT}
    bot = _build_bot_mock()

    widget = _DummyWidget(
        message=message,
        bot=bot,
        command="/dummy",
        result_mode=WIDGET_RESULT_MODE_MESSAGE,
    )

    assert widget.result_mode == WIDGET_RESULT_MODE_MESSAGE


def test__result_mode_parsing__supports_aliases_and_plain_tokens() -> None:
    assert _normalize_result_mode(" INLINE ") == WIDGET_RESULT_MODE_EDIT
    assert _parse_result_mode_from_argument("reply remaining") == WIDGET_RESULT_MODE_MESSAGE
