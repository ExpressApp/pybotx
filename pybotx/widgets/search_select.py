from pybotx.bot.bot import Bot
from pybotx.models.message.incoming_message import IncomingMessage

from .base import WidgetResultMode
from .markup import MessageMarkup
from .select import SELECT_VALUE_KEY, SelectOption, SelectWidget, _normalize_option

SEARCH_QUERY_KEY = "search_query"
SEARCH_PAGE_KEY = "search_page"


def _safe_page(value: object) -> int:
    if isinstance(value, int) and value >= 0:
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    return 0


class SearchSelectWidget(SelectWidget):
    def __init__(
        self,
        options: list[str | SelectOption],
        label: str,
        page_size: int = 5,
        empty_label: str = "Ничего не найдено",
        selected_prefix: str = "• ",
        *,
        message: IncomingMessage,
        bot: Bot,
        command: str,
        additional_markup: MessageMarkup | None = None,
        result_mode: WidgetResultMode | None = None,
    ) -> None:
        super().__init__(
            options=options,
            label=label,
            selected_prefix=selected_prefix,
            message=message,
            bot=bot,
            command=command,
            additional_markup=additional_markup,
            result_mode=result_mode,
        )
        self.page_size = max(page_size, 1)
        self.empty_label = empty_label

        self.query = str(
            self.message.data.get(SEARCH_QUERY_KEY, self.message.argument),
        ).strip()
        self.page = _safe_page(self.message.data.get(SEARCH_PAGE_KEY))

        self.all_options = [_normalize_option(option) for option in options]
        self.filtered_options = self._filter_options()
        self.page = min(self.page, self._max_page())
        self.displayed_options = self._slice_page()
        self.widget_message.body = self._compose_body(label)

    def add_markup(self) -> None:
        if not self.displayed_options:
            self.widget_bubbles.add_button(
                command=self.command,
                label=self.empty_label,
                data={SEARCH_QUERY_KEY: "", SEARCH_PAGE_KEY: 0},
            )
            self.add_additional_markup()
            return

        for option in self.displayed_options:
            self.widget_bubbles.add_button(
                command=self.command,
                label=option.label,
                data={SELECT_VALUE_KEY: option.value},
            )

        if self.page > 0:
            self.widget_bubbles.add_button(
                command=self.command,
                label="Назад",
                data={SEARCH_QUERY_KEY: self.query, SEARCH_PAGE_KEY: self.page - 1},
            )

        if self.page < self._max_page():
            self.widget_bubbles.add_button(
                command=self.command,
                label="Вперед",
                data={SEARCH_QUERY_KEY: self.query, SEARCH_PAGE_KEY: self.page + 1},
                new_row=self.page == 0,
            )

        self.add_additional_markup()

    def _filter_options(self) -> list[SelectOption]:
        if not self.query:
            return self.all_options

        query_lower = self.query.lower()
        return [
            option
            for option in self.all_options
            if query_lower in option.label.lower() or query_lower in option.value.lower()
        ]

    def _max_page(self) -> int:
        if not self.filtered_options:
            return 0

        return (len(self.filtered_options) - 1) // self.page_size

    def _slice_page(self) -> list[SelectOption]:
        start = self.page * self.page_size
        end = start + self.page_size
        return self.filtered_options[start:end]

    def _compose_body(self, label: str) -> str:
        if not self.query:
            return label

        return f"{label}\nПоиск: {self.query}"
