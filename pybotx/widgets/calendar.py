from calendar import Calendar
from datetime import date, datetime
from typing import Any

from pybotx.bot.bot import Bot
from pybotx.models.message.incoming_message import IncomingMessage

from . import strings
from .base import Widget
from .markup import MessageMarkup
from .service import send_or_update_message

MONTH_TO_DISPLAY_KEY = "calendar_month_to_display"
SELECTED_DATE_KEY = "calendar_selected_date"


def _parse_date(value: object) -> date | None:
    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        pass

    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


class CalendarWidget(Widget):
    LEFT_ARROW = strings.LEFT_ARROW
    RIGHT_ARROW = strings.RIGHT_ARROW
    AFTER_SELECT_TEXT = strings.CAL_DATE_SELECTED
    SELECT_DATE = strings.SELECT_DATE
    WEEKDAYS = strings.WEEKDAYS
    MONTHS = strings.MONTHS

    def __init__(
        self,
        start_date: date | None = None,
        end_date: date = date.max,
        include_past: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.start_date = start_date or date.today()
        self.end_date = end_date
        self.include_past = include_past

        if self.start_date > self.end_date:
            raise ValueError("'start_date' should be less or equal than 'end_date'")

        self.month_to_display = self.message.data.get(MONTH_TO_DISPLAY_KEY)
        self.widget_message.body = self.SELECT_DATE
        self.current_date = self.get_current_date()

    @classmethod
    async def get_value(
        cls,
        message: IncomingMessage,
        bot: Bot,
        *,
        send_feedback: bool = True,
    ) -> date:
        selected_date = _parse_date(message.data.get(SELECTED_DATE_KEY))
        if selected_date is None:
            raise RuntimeError("Date is not selected.")

        _clear_calendar_data(message)
        if send_feedback:
            await send_or_update_message(message, bot, cls.AFTER_SELECT_TEXT, MessageMarkup())
        return selected_date

    def get_current_date(self) -> date:
        is_navigation = (
            self.LEFT_ARROW in self.message.argument
            or self.RIGHT_ARROW in self.message.argument
        )

        if is_navigation and self.month_to_display:
            parsed_date = _parse_date(self.month_to_display)
            if parsed_date is not None:
                return parsed_date.replace(day=1)

        return date.today().replace(day=1)

    def get_prev_and_next_year(self) -> tuple[date, date]:
        month = 1 if self.include_past else date.today().month
        prev_year = date(self.current_date.year - 1, month, 1)
        next_year = date(self.current_date.year + 1, 1, 1)
        return prev_year, next_year

    def get_prev_and_next_month(self) -> tuple[date, date]:
        if self.current_date.month == 1:
            prev_month = date(self.current_date.year - 1, 12, 1)
        else:
            prev_month = date(self.current_date.year, self.current_date.month - 1, 1)

        if self.current_date.month == 12:
            next_month = date(self.current_date.year + 1, 1, 1)
        else:
            next_month = date(self.current_date.year, self.current_date.month + 1, 1)

        return prev_month, next_month

    def add_markup(self) -> None:
        self.add_year_bubbles()
        self.add_month_bubbles()
        self.add_week_bubbles()
        self.add_day_bubbles()
        self.add_additional_markup()

    def add_year_bubbles(self) -> None:
        prev_year, next_year = self.get_prev_and_next_year()
        can_show_prev_year = (
            self.include_past or self.start_date.year < self.current_date.year
        )
        can_show_next_year = self.current_date.year < self.end_date.year

        if can_show_prev_year:
            self.widget_bubbles.add_button(
                command=f"{self.command} {self.LEFT_ARROW}",
                label=self.LEFT_ARROW,
                data={MONTH_TO_DISPLAY_KEY: prev_year.isoformat()},
            )
        else:
            self.widget_bubbles.add_button(command="", label=" ")

        self.widget_bubbles.add_button(
            command="",
            label=str(self.current_date.year),
            new_row=False,
        )

        if can_show_next_year:
            self.widget_bubbles.add_button(
                command=f"{self.command} {self.RIGHT_ARROW}",
                label=self.RIGHT_ARROW,
                data={MONTH_TO_DISPLAY_KEY: next_year.isoformat()},
                new_row=False,
            )
        else:
            self.widget_bubbles.add_button(
                command="",
                label=" ",
                new_row=False,
            )

    def add_month_bubbles(self) -> None:
        prev_month, next_month = self.get_prev_and_next_month()
        is_lower_limit = all(
            (
                self.start_date.month >= self.current_date.month,
                self.start_date.year >= self.current_date.year,
            )
        )
        is_upper_limit = all(
            (
                self.end_date.month == self.current_date.month,
                self.end_date.year == self.current_date.year,
            )
        )

        if not self.include_past and is_lower_limit:
            self.widget_bubbles.add_button(command="", label=" ")
        else:
            self.widget_bubbles.add_button(
                command=f"{self.command} {self.LEFT_ARROW}",
                label=self.LEFT_ARROW,
                data={MONTH_TO_DISPLAY_KEY: prev_month.isoformat()},
            )

        self.widget_bubbles.add_button(
            command="",
            label=self.MONTHS[self.current_date.month],
            new_row=False,
        )

        if is_upper_limit:
            self.widget_bubbles.add_button(
                command="",
                label=" ",
                new_row=False,
            )
        else:
            self.widget_bubbles.add_button(
                command=f"{self.command} {self.RIGHT_ARROW}",
                label=self.RIGHT_ARROW,
                data={MONTH_TO_DISPLAY_KEY: next_month.isoformat()},
                new_row=False,
            )

    def add_week_bubbles(self) -> None:
        for idx, weekday in enumerate(self.WEEKDAYS):
            self.widget_bubbles.add_button(
                command="",
                label=weekday,
                new_row=idx == 0,
            )

    def add_day_bubbles(self) -> None:
        weeks = Calendar().monthdatescalendar(
            year=self.current_date.year,
            month=self.current_date.month,
        )

        for calendar_row, week in enumerate(weeks, 1):
            row_data: list[tuple[str, str, dict[str, str]]] = []
            append_row = False

            for calendar_date in week:
                show_day = not any(
                    (
                        not self.include_past and calendar_date < self.start_date,
                        calendar_date > self.end_date,
                        calendar_row == len(weeks) and calendar_date.day < 7,
                        calendar_row == 1 and calendar_date.day > 7,
                    )
                )

                if show_day:
                    label = str(calendar_date.day)
                    command = f"{self.command} {calendar_date.isoformat()}"
                    payload = {SELECTED_DATE_KEY: calendar_date.isoformat()}
                    append_row = True
                else:
                    label = ""
                    command = ""
                    payload = {}

                row_data.append((command, label, payload))

            if not append_row:
                continue

            for button_idx, (command, label, payload) in enumerate(row_data):
                self.widget_bubbles.add_button(
                    command=command,
                    label=label,
                    data=payload,
                    new_row=button_idx == 0,
                )


def _clear_calendar_data(message: IncomingMessage) -> None:
    for metadata in (message.data, message.metadata):
        metadata.pop(MONTH_TO_DISPLAY_KEY, None)
        metadata.pop(SELECTED_DATE_KEY, None)
