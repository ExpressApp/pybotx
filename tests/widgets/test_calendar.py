from datetime import date
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.base import PYBOTX_WIDGET_FLAG
from pybotx.widgets.calendar import (
    MONTH_TO_DISPLAY_KEY,
    SELECTED_DATE_KEY,
    CalendarWidget,
    _parse_date,
)


def _build_bot_mock() -> Any:
    return SimpleNamespace(
        send=AsyncMock(return_value=uuid4()),
        edit_message=AsyncMock(),
    )


@pytest.mark.asyncio
async def test__calendar_widget__display(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = CalendarWidget(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        include_past=True,
        message=message,
        bot=bot,
        command="/calendar",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]

    assert sent_message.body == "Выберите дату"
    assert "Пн" in labels
    assert any(month in labels for month in CalendarWidget.MONTHS.values())


def test__calendar_widget__invalid_dates(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    with pytest.raises(ValueError):
        CalendarWidget(
            start_date=date(2026, 2, 1),
            end_date=date(2026, 1, 1),
            message=message,
            bot=bot,
            command="/calendar",
        )


def test__calendar_widget__get_current_date_from_navigation(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory(body="/calendar ⬅️")
    message.data = {MONTH_TO_DISPLAY_KEY: "2026-05-01"}
    bot = _build_bot_mock()

    widget = CalendarWidget(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        message=message,
        bot=bot,
        command="/calendar",
    )

    assert widget.current_date == date(2026, 5, 1)


def test__calendar_widget__prev_next_helpers(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = CalendarWidget(
        include_past=True,
        message=message,
        bot=bot,
        command="/calendar",
    )
    widget.current_date = date(2026, 6, 1)

    assert widget.get_prev_and_next_year() == (date(2025, 1, 1), date(2027, 1, 1))
    assert widget.get_prev_and_next_month() == (date(2026, 5, 1), date(2026, 7, 1))


@pytest.mark.asyncio
async def test__calendar_widget__get_value_update(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {SELECTED_DATE_KEY: "2026-01-15"}
    message.metadata = {
        PYBOTX_WIDGET_FLAG: 1,
        MONTH_TO_DISPLAY_KEY: "2026-01-01",
    }
    message.source_sync_id = uuid4()
    bot = _build_bot_mock()

    selected_date = await CalendarWidget.get_value(message, bot)

    assert selected_date == date(2026, 1, 15)
    assert bot.edit_message.await_count == 1
    assert SELECTED_DATE_KEY not in message.data
    assert MONTH_TO_DISPLAY_KEY not in message.metadata


@pytest.mark.asyncio
async def test__calendar_widget__get_value_without_feedback(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {SELECTED_DATE_KEY: "2026-01-15"}
    message.metadata = {
        PYBOTX_WIDGET_FLAG: 1,
        MONTH_TO_DISPLAY_KEY: "2026-01-01",
    }
    message.source_sync_id = uuid4()
    bot = _build_bot_mock()

    selected_date = await CalendarWidget.get_value(
        message,
        bot,
        send_feedback=False,
    )

    assert selected_date == date(2026, 1, 15)
    assert bot.edit_message.await_count == 0
    assert bot.send.await_count == 0
    assert SELECTED_DATE_KEY not in message.data
    assert MONTH_TO_DISPLAY_KEY not in message.metadata


@pytest.mark.asyncio
async def test__calendar_widget__get_value_error(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    with pytest.raises(RuntimeError):
        await CalendarWidget.get_value(message, bot)


def test__calendar_widget__parse_date() -> None:
    assert _parse_date(date(2026, 1, 1)) == date(2026, 1, 1)
    assert _parse_date("2026-01-15") == date(2026, 1, 15)
    assert _parse_date("2026-01-15T10:00:00") == date(2026, 1, 15)
    assert _parse_date("bad-date") is None
    assert _parse_date(42) is None


def test__calendar_widget__navigation_with_invalid_month_value(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory(body="/calendar ⬅️")
    message.data = {MONTH_TO_DISPLAY_KEY: "bad-date"}
    bot = _build_bot_mock()

    widget = CalendarWidget(
        message=message,
        bot=bot,
        command="/calendar",
    )

    assert widget.current_date == date.today().replace(day=1)


def test__calendar_widget__month_boundaries(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    widget = CalendarWidget(message=message, bot=bot, command="/calendar")

    widget.current_date = date(2026, 1, 1)
    assert widget.get_prev_and_next_month() == (date(2025, 12, 1), date(2026, 2, 1))

    widget.current_date = date(2026, 12, 1)
    assert widget.get_prev_and_next_month() == (date(2026, 11, 1), date(2027, 1, 1))


def test__calendar_widget__year_and_month_arrow_visibility(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    widget = CalendarWidget(
        start_date=date(2026, 2, 1),
        end_date=date(2027, 2, 1),
        include_past=False,
        message=message,
        bot=bot,
        command="/calendar",
    )
    widget.current_date = date(2026, 2, 1)
    widget.add_year_bubbles()
    widget.add_month_bubbles()

    labels = [button.label for row in widget.widget_bubbles for button in row]
    assert labels.count(" ") >= 2
    assert "➡️" in labels

    upper_limit_widget = CalendarWidget(
        start_date=date(2026, 2, 1),
        end_date=date(2026, 2, 28),
        include_past=False,
        message=message,
        bot=bot,
        command="/calendar",
    )
    upper_limit_widget.current_date = date(2026, 2, 1)
    upper_limit_widget.add_month_bubbles()

    month_labels = [
        button.label for row in upper_limit_widget.widget_bubbles for button in row
    ]
    assert month_labels[-1] == " "


def test__calendar_widget__day_bubbles_with_visible_days(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    widget = CalendarWidget(
        start_date=date(2026, 2, 1),
        end_date=date(2026, 2, 28),
        include_past=True,
        message=message,
        bot=bot,
        command="/calendar",
    )
    widget.current_date = date(2026, 2, 1)
    widget.add_day_bubbles()

    labels = [button.label for row in widget.widget_bubbles for button in row]
    assert "1" in labels
