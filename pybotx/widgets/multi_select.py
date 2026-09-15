from typing import Any

from pybotx.models.message.incoming_message import IncomingMessage

from .base import Widget
from .select import SelectOption, _normalize_option
from .strings import CHECKBOX_CHECKED, CHECKBOX_UNCHECKED

MULTI_SELECT_VALUE_KEY = "multi_select_value"
MULTI_SELECTED_VALUES_KEY = "multi_selected_values"


def _coerce_str_list(raw_values: object) -> list[str]:
    if not isinstance(raw_values, list):
        return []

    return [str(value) for value in raw_values]


class MultiSelectWidget(Widget):
    def __init__(
        self,
        options: list[str | SelectOption],
        label: str,
        max_selected: int | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.options = [_normalize_option(option) for option in options]
        self.max_selected = max_selected
        self.widget_message.body = label

        self.selected_values = _coerce_str_list(
            self.message.metadata.get(MULTI_SELECTED_VALUES_KEY),
        )
        self._toggle_value_from_data()
        self.widget_metadata[MULTI_SELECTED_VALUES_KEY] = self.selected_values

    def add_markup(self) -> None:
        for option in self.options:
            checkbox = CHECKBOX_UNCHECKED
            if option.value in self.selected_values:
                checkbox = CHECKBOX_CHECKED

            self.widget_bubbles.add_button(
                command=self.command,
                label=f"{checkbox} {option.label}",
                data={MULTI_SELECT_VALUE_KEY: option.value},
            )

        self.add_additional_markup()

    def _toggle_value_from_data(self) -> None:
        clicked_value = self.message.data.get(MULTI_SELECT_VALUE_KEY)
        if clicked_value is None:
            return

        clicked_str = str(clicked_value)
        if clicked_str in self.selected_values:
            self.selected_values.remove(clicked_str)
            return

        if self.max_selected is not None and len(self.selected_values) >= self.max_selected:
            return

        self.selected_values.append(clicked_str)

    @classmethod
    def get_selected_values(cls, message: IncomingMessage) -> list[str]:
        return _coerce_str_list(message.metadata.get(MULTI_SELECTED_VALUES_KEY))
