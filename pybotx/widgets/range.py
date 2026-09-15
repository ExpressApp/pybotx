from collections.abc import Sequence
from typing import Any

from pybotx.models.message.incoming_message import IncomingMessage

from .base import Widget

CURRENT_INDEX_KEY = "range_current_index"
ELEMENTS_KEY = "range_elements"


def _safe_index(value: Any, default: int = 0) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    return default


class RangeWidget(Widget):
    def __init__(
        self,
        elements: Sequence[str] | None = None,
        label_template: str = "Current element: {element}",
        forward_label: str = "Вперед",
        backward_label: str = "Назад",
        empty_body: str = "Список пуст",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.label_template = label_template
        self.forward_label = forward_label
        self.backward_label = backward_label
        self.empty_body = empty_body

        if elements is None:
            incoming_elements = self.message.metadata.get(ELEMENTS_KEY, [])
            if not isinstance(incoming_elements, list):
                incoming_elements = []
            self.elements = [str(element) for element in incoming_elements]
        else:
            self.elements = [str(element) for element in elements]

        if not self.elements:
            self.current_index = 0
            self.widget_message.body = self.empty_body
            return

        current_index = _safe_index(self.message.data.get(CURRENT_INDEX_KEY))
        if current_index < 0:
            current_index = 0
        if current_index >= len(self.elements):
            current_index = len(self.elements) - 1

        self.current_index = current_index
        self.widget_message.body = self.label_template.format(
            element=self.elements[self.current_index],
            index=self.current_index + 1,
            total=len(self.elements),
        )
        self.widget_metadata[ELEMENTS_KEY] = self.elements

    def add_markup(self) -> None:
        if not self.elements:
            self.add_additional_markup()
            return

        if self.current_index > 0:
            self.widget_bubbles.add_button(
                command=self.command,
                label=self.backward_label,
                data={CURRENT_INDEX_KEY: self.current_index - 1},
            )

        if self.current_index < len(self.elements) - 1:
            self.widget_bubbles.add_button(
                command=self.command,
                label=self.forward_label,
                data={CURRENT_INDEX_KEY: self.current_index + 1},
                new_row=self.current_index == 0,
            )

        self.add_additional_markup()

    @classmethod
    def get_value(cls, message: IncomingMessage) -> str:
        elements = message.metadata.get(ELEMENTS_KEY, [])
        if not isinstance(elements, list) or not elements:
            raise RuntimeError("Range elements are not found in metadata.")

        current_index = _safe_index(message.data.get(CURRENT_INDEX_KEY))
        if current_index < 0 or current_index >= len(elements):
            raise RuntimeError("Current index is out of range.")

        return str(elements[current_index])
