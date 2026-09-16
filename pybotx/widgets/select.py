from dataclasses import dataclass
from typing import Any

from pybotx.models.message.incoming_message import IncomingMessage

from .base import Widget

SELECT_VALUE_KEY = "select_value"


@dataclass(frozen=True, slots=True)
class SelectOption:
    value: str
    label: str


def _normalize_option(raw_option: str | SelectOption) -> SelectOption:
    if isinstance(raw_option, SelectOption):
        return raw_option

    value = str(raw_option)
    return SelectOption(value=value, label=value)


class SelectWidget(Widget):
    def __init__(
        self,
        options: list[str | SelectOption],
        label: str,
        selected_prefix: str = "• ",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.options = [_normalize_option(option) for option in options]
        self.selected_prefix = selected_prefix
        self.selected_value = self.message.data.get(SELECT_VALUE_KEY)
        self.widget_message.body = label

    def add_markup(self) -> None:
        for option in self.options:
            label = option.label
            if self.selected_value == option.value:
                label = f"{self.selected_prefix}{label}"

            self.widget_bubbles.add_button(
                command=self.command,
                label=label,
                data={SELECT_VALUE_KEY: option.value},
            )

        self.add_additional_markup()

    @classmethod
    def get_value(cls, message: IncomingMessage) -> str:
        selected_value = message.data.get(SELECT_VALUE_KEY)
        if selected_value is None:
            raise RuntimeError("Selected value is not found.")

        return str(selected_value)
