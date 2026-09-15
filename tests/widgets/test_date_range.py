from datetime import date
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.date_range import (
    DATE_RANGE_ACTION_KEY,
    DATE_RANGE_ACTION_RESET,
    DATE_RANGE_CURSOR_KEY,
    DATE_RANGE_END_KEY,
    DATE_RANGE_SELECTED_DATE_KEY,
    DATE_RANGE_START_KEY,
    DateRangeWidget,
    _parse_iso_date,
    _serialize_date,
)


def _build_bot_mock() -> Any:
    return SimpleNamespace(send=AsyncMock(return_value=uuid4()), edit_message=AsyncMock())


def test__date_range_widget__helpers() -> None:
    assert _parse_iso_date(date(2026, 1, 1)) == date(2026, 1, 1)
    assert _parse_iso_date("2026-01-01") == date(2026, 1, 1)
    assert _parse_iso_date("bad") is None
    assert _parse_iso_date(1) is None
    assert _serialize_date(date(2026, 1, 1)) == "2026-01-01"
    assert _serialize_date(None) is None


@pytest.mark.asyncio
async def test__date_range_widget__start_cursor(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = DateRangeWidget(message=message, bot=bot, command="/date-range")
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["Сегодня", "Завтра"]


@pytest.mark.asyncio
async def test__date_range_widget__select_start_then_end(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {DATE_RANGE_SELECTED_DATE_KEY: "2026-02-10"}
    bot = _build_bot_mock()

    widget = DateRangeWidget(message=message, bot=bot, command="/date-range")
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.metadata[DATE_RANGE_CURSOR_KEY] == "end"
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["+1 дн.", "+7 дн.", "+30 дн.", "Сбросить"]

    message.metadata = {
        DATE_RANGE_START_KEY: "2026-02-10",
        DATE_RANGE_CURSOR_KEY: "end",
    }
    message.data = {DATE_RANGE_SELECTED_DATE_KEY: "2026-02-08"}
    widget = DateRangeWidget(message=message, bot=bot, command="/date-range")
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.metadata[DATE_RANGE_START_KEY] == "2026-02-08"
    assert sent_message.metadata[DATE_RANGE_END_KEY] == "2026-02-10"
    assert sent_message.metadata[DATE_RANGE_CURSOR_KEY] == "done"
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["Сбросить"]

    message.metadata = {
        DATE_RANGE_START_KEY: "2026-02-08",
        DATE_RANGE_CURSOR_KEY: "end",
    }
    message.data = {DATE_RANGE_SELECTED_DATE_KEY: "2026-02-12"}
    widget = DateRangeWidget(message=message, bot=bot, command="/date-range")
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.metadata[DATE_RANGE_START_KEY] == "2026-02-08"
    assert sent_message.metadata[DATE_RANGE_END_KEY] == "2026-02-12"


@pytest.mark.asyncio
async def test__date_range_widget__reset_action(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.metadata = {
        DATE_RANGE_START_KEY: "2026-01-01",
        DATE_RANGE_END_KEY: "2026-01-10",
        DATE_RANGE_CURSOR_KEY: "done",
    }
    message.data = {DATE_RANGE_ACTION_KEY: DATE_RANGE_ACTION_RESET}
    bot = _build_bot_mock()

    widget = DateRangeWidget(message=message, bot=bot, command="/date-range")
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.metadata[DATE_RANGE_START_KEY] is None
    assert sent_message.metadata[DATE_RANGE_CURSOR_KEY] == "start"


def test__date_range_widget__get_value(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.metadata = {
        DATE_RANGE_START_KEY: "2026-01-01",
        DATE_RANGE_END_KEY: "2026-01-10",
    }
    assert DateRangeWidget.get_value(message) == (date(2026, 1, 1), date(2026, 1, 10))

    message.metadata = {DATE_RANGE_START_KEY: "2026-01-01"}
    with pytest.raises(RuntimeError):
        DateRangeWidget.get_value(message)
