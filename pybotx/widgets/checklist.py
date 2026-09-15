from collections.abc import Iterable, Sequence
from typing import Any

from . import strings
from .base import Widget

SELECTED_ITEM_KEY = "checklist_selected_item"
CHECKED_ITEMS_KEY = "checklist_checked_items"


class CheckListWidget(Widget):
    def __init__(
        self,
        widget_content: Sequence[Any],
        label: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.widget_content = widget_content
        self.widget_message.body = label

        self.checked_items = list(self.message.metadata.get(CHECKED_ITEMS_KEY, []))
        self._toggle_checked_item()

    @classmethod
    def get_value(cls, message: Any) -> Any:
        return message.data[SELECTED_ITEM_KEY]

    @classmethod
    def get_checked_items(cls, message: Any) -> list[Any]:
        return list(message.metadata.get(CHECKED_ITEMS_KEY, []))

    def add_markup(self) -> None:
        for content_item in self.widget_content:
            if isinstance(content_item, (list, tuple, set)):
                self._add_row(content_item)
                continue
            self._add_button(content_item)

        self.add_additional_markup()

    def _toggle_checked_item(self) -> None:
        if SELECTED_ITEM_KEY not in self.message.data:
            return

        selected_item = self.message.data[SELECTED_ITEM_KEY]
        if selected_item in self.checked_items:
            self.checked_items.remove(selected_item)
        else:
            self.checked_items.append(selected_item)

        self.widget_metadata[CHECKED_ITEMS_KEY] = self.checked_items

    def _add_row(self, row: Iterable[Any]) -> None:
        for row_idx, row_item in enumerate(row):
            self.widget_bubbles.add_button(
                command=self.command,
                label=self._checkbox_label(row_item),
                data={SELECTED_ITEM_KEY: row_item},
                new_row=row_idx == 0,
            )

    def _add_button(self, item: Any) -> None:
        self.widget_bubbles.add_button(
            command=self.command,
            label=self._checkbox_label(item),
            data={SELECTED_ITEM_KEY: item},
        )

    def _checkbox_label(self, content_item: Any) -> str:
        checkbox = strings.CHECKBOX_UNCHECKED
        if content_item in self.checked_items:
            checkbox = strings.CHECKBOX_CHECKED

        return f"{checkbox} {content_item}"
