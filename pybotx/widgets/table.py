from typing import Any

from .base import Widget

TABLE_PAGE_KEY = "table_page"
TABLE_SORT_KEY = "table_sort"
TABLE_DESC_KEY = "table_desc"
TABLE_QUERY_KEY = "table_query"


def _safe_int(value: object) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    return 0


def _safe_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() in {"true", "1", "yes"}

    return False


class TableWidget(Widget):
    def __init__(
        self,
        rows: list[dict[str, Any]],
        columns: list[str],
        label: str = "Таблица",
        page_size: int = 5,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.rows = rows
        self.columns = columns
        self.label = label
        self.page_size = max(page_size, 1)

        self.query = str(self.message.data.get(TABLE_QUERY_KEY, self.message.argument)).strip()
        self.sort_by = str(
            self.message.data.get(TABLE_SORT_KEY, self.message.metadata.get(TABLE_SORT_KEY, "")),
        )
        if self.sort_by not in self.columns and self.columns:
            self.sort_by = self.columns[0]

        self.sort_desc = _safe_bool(
            self.message.data.get(TABLE_DESC_KEY, self.message.metadata.get(TABLE_DESC_KEY, False)),
        )
        self.page = _safe_int(
            self.message.data.get(TABLE_PAGE_KEY, self.message.metadata.get(TABLE_PAGE_KEY, 0)),
        )

        self.filtered_rows = self._filter_rows()
        self.sorted_rows = self._sort_rows()
        self.page = min(max(self.page, 0), self._max_page())
        self.page_rows = self._slice_rows()

        self.widget_message.body = self._build_body()
        self._sync_metadata()

    def add_markup(self) -> None:
        if self.page > 0:
            self.widget_bubbles.add_button(
                command=self.command,
                label="Назад",
                data=self._state_data(page=self.page - 1),
            )

        if self.page < self._max_page():
            self.widget_bubbles.add_button(
                command=self.command,
                label="Вперед",
                data=self._state_data(page=self.page + 1),
                new_row=self.page == 0,
            )

        for index, column in enumerate(self.columns):
            next_desc = self.sort_desc
            if column == self.sort_by:
                next_desc = not self.sort_desc

            self.widget_bubbles.add_button(
                command=self.command,
                label=f"Сорт: {column}",
                data=self._state_data(
                    page=0,
                    sort_by=column,
                    desc=next_desc,
                ),
                new_row=index == 0,
            )

        if self.query:
            self.widget_bubbles.add_button(
                command=self.command,
                label="Сбросить фильтр",
                data=self._state_data(query="", page=0),
            )

        self.add_additional_markup()

    def _filter_rows(self) -> list[dict[str, Any]]:
        if not self.query:
            return self.rows

        query_lower = self.query.lower()
        return [
            row
            for row in self.rows
            if any(query_lower in str(row.get(column, "")).lower() for column in self.columns)
        ]

    def _sort_rows(self) -> list[dict[str, Any]]:
        if not self.sort_by:
            return self.filtered_rows

        return sorted(
            self.filtered_rows,
            key=lambda row: str(row.get(self.sort_by, "")).lower(),
            reverse=self.sort_desc,
        )

    def _max_page(self) -> int:
        if not self.sorted_rows:
            return 0

        return (len(self.sorted_rows) - 1) // self.page_size

    def _slice_rows(self) -> list[dict[str, Any]]:
        left = self.page * self.page_size
        right = left + self.page_size
        return self.sorted_rows[left:right]

    def _build_body(self) -> str:
        lines = [self.label]
        if self.query:
            lines.append(f"Фильтр: {self.query}")

        if not self.page_rows:
            lines.append("Нет данных")
            return "\n".join(lines)

        lines.append(" | ".join(self.columns))
        for row in self.page_rows:
            lines.append(" | ".join(str(row.get(column, "")) for column in self.columns))

        return "\n".join(lines)

    def _state_data(
        self,
        *,
        page: int | None = None,
        sort_by: str | None = None,
        desc: bool | None = None,
        query: str | None = None,
    ) -> dict[str, Any]:
        return {
            TABLE_PAGE_KEY: self.page if page is None else page,
            TABLE_SORT_KEY: self.sort_by if sort_by is None else sort_by,
            TABLE_DESC_KEY: self.sort_desc if desc is None else desc,
            TABLE_QUERY_KEY: self.query if query is None else query,
        }

    def _sync_metadata(self) -> None:
        self.widget_metadata[TABLE_PAGE_KEY] = self.page
        self.widget_metadata[TABLE_SORT_KEY] = self.sort_by
        self.widget_metadata[TABLE_DESC_KEY] = self.sort_desc
        self.widget_metadata[TABLE_QUERY_KEY] = self.query
