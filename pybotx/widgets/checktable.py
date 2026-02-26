from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, model_validator

from . import strings
from .base import Widget
from .undefined import Undefined, undefined

T = TypeVar("T")


class CheckboxContent(BaseModel, Generic[T]):
    label: str
    command: str
    checkbox_value: T | Undefined | None = undefined
    mapping: dict[T, str] | None = None
    data: dict[str, Any] | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_checkbox_value(self) -> "CheckboxContent[T]":
        if (
            self.mapping
            and not isinstance(self.checkbox_value, Undefined)
            and self.checkbox_value not in self.mapping
        ):
            msg = f"'mapping' should contain 'checkbox_value' - '{self.checkbox_value}'"
            raise ValueError(msg)
        return self


class ChecktableWidget(Widget):
    def __init__(
        self,
        checkboxes: list[CheckboxContent[Any]],
        label: str,
        uncheck_command: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.checkboxes = checkboxes
        self.uncheck_command = uncheck_command
        self.widget_message.body = label

    def add_markup(self) -> None:
        for checkbox in self.checkboxes:
            payload = checkbox.data or {}
            checkbox_status = strings.CHECKBOX_UNCHECKED

            if not isinstance(checkbox.checkbox_value, Undefined):
                checkbox_status = strings.CHECKBOX_CHECKED

            self.widget_bubbles.add_button(
                command=self.uncheck_command,
                label=f"{checkbox_status} {checkbox.label}",
                data=payload,
            )
            self.widget_bubbles.add_button(
                command=checkbox.command,
                label=self._checkbox_value_text(checkbox),
                data=payload,
                new_row=False,
            )

        self.add_additional_markup()

    def _checkbox_value_text(self, checkbox: CheckboxContent[Any]) -> str:
        if checkbox.checkbox_value is None:
            return strings.EMPTY

        is_undefined = isinstance(checkbox.checkbox_value, Undefined)
        if checkbox.mapping:
            if is_undefined:
                return strings.CHOOSE_LABEL
            return checkbox.mapping[checkbox.checkbox_value]

        if is_undefined:
            return strings.FILL_LABEL

        return str(checkbox.checkbox_value)
