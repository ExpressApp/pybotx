from datetime import date, timedelta
from typing import Any

from pybotx.models.message.incoming_message import IncomingMessage

from .base import Widget

DATE_RANGE_START_KEY = "date_range_start"
DATE_RANGE_END_KEY = "date_range_end"
DATE_RANGE_CURSOR_KEY = "date_range_cursor"
DATE_RANGE_SELECTED_DATE_KEY = "date_range_selected_date"
DATE_RANGE_ACTION_KEY = "date_range_action"
DATE_RANGE_ACTION_RESET = "reset"


def _parse_iso_date(value: object) -> date | None:
    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _serialize_date(value: date | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


class DateRangeWidget(Widget):
    def __init__(
        self,
        label: str = "Выбор периода",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.label = label
        self.start = _parse_iso_date(self.message.metadata.get(DATE_RANGE_START_KEY))
        self.end = _parse_iso_date(self.message.metadata.get(DATE_RANGE_END_KEY))
        self.cursor = str(self.message.metadata.get(DATE_RANGE_CURSOR_KEY, "start"))
        self._apply_action()
        self._apply_selected_date()
        self._sync_metadata()
        self.widget_message.body = self._build_body()

    def add_markup(self) -> None:
        if self.cursor == "start":
            self._add_start_buttons()
            self.add_additional_markup()
            return

        if self.cursor == "end" and self.start is not None:
            for days in (1, 7, 30):
                suggested_date = self.start + timedelta(days=days)
                self.widget_bubbles.add_button(
                    command=self.command,
                    label=f"+{days} дн.",
                    data={DATE_RANGE_SELECTED_DATE_KEY: suggested_date.isoformat()},
                    new_row=days == 1,
                )
            self._add_reset_button(new_row=True)
            self.add_additional_markup()
            return

        self._add_reset_button()
        self.add_additional_markup()

    @classmethod
    def get_value(cls, message: IncomingMessage) -> tuple[date, date]:
        start = _parse_iso_date(message.metadata.get(DATE_RANGE_START_KEY))
        end = _parse_iso_date(message.metadata.get(DATE_RANGE_END_KEY))
        if start is None or end is None:
            raise RuntimeError("Date range is incomplete.")

        return start, end

    def _apply_action(self) -> None:
        if self.message.data.get(DATE_RANGE_ACTION_KEY) != DATE_RANGE_ACTION_RESET:
            return

        self.start = None
        self.end = None
        self.cursor = "start"

    def _apply_selected_date(self) -> None:
        selected_date = _parse_iso_date(self.message.data.get(DATE_RANGE_SELECTED_DATE_KEY))
        if selected_date is None:
            return

        if self.start is None or self.cursor == "start":
            self.start = selected_date
            self.end = None
            self.cursor = "end"
            return

        self.end = selected_date
        if self.end < self.start:
            self.start, self.end = self.end, self.start
        self.cursor = "done"

    def _sync_metadata(self) -> None:
        self.widget_metadata[DATE_RANGE_START_KEY] = _serialize_date(self.start)
        self.widget_metadata[DATE_RANGE_END_KEY] = _serialize_date(self.end)
        self.widget_metadata[DATE_RANGE_CURSOR_KEY] = self.cursor

    def _build_body(self) -> str:
        start = _serialize_date(self.start) or "—"
        end = _serialize_date(self.end) or "—"
        return f"{self.label}\nНачало: {start}\nКонец: {end}"

    def _add_start_buttons(self) -> None:
        today = date.today()
        self.widget_bubbles.add_button(
            command=self.command,
            label="Сегодня",
            data={DATE_RANGE_SELECTED_DATE_KEY: today.isoformat()},
        )
        self.widget_bubbles.add_button(
            command=self.command,
            label="Завтра",
            data={DATE_RANGE_SELECTED_DATE_KEY: (today + timedelta(days=1)).isoformat()},
            new_row=False,
        )

    def _add_reset_button(self, *, new_row: bool = False) -> None:
        self.widget_bubbles.add_button(
            command=self.command,
            label="Сбросить",
            data={DATE_RANGE_ACTION_KEY: DATE_RANGE_ACTION_RESET},
            new_row=new_row,
        )
