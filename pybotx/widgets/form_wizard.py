from dataclasses import dataclass
from typing import Any

from pybotx.models.message.incoming_message import IncomingMessage

from .base import Widget

FORM_STEP_INDEX_KEY = "form_step_index"
FORM_VALUES_KEY = "form_values"
FORM_ACTION_KEY = "form_action"
FORM_INPUT_KEY = "form_input"

FORM_ACTION_NEXT = "next"
FORM_ACTION_BACK = "back"
FORM_ACTION_CANCEL = "cancel"
FORM_ACTION_RESET = "reset"


@dataclass(frozen=True, slots=True)
class FormWizardStep:
    field: str
    label: str


def _safe_index(value: object, default: int = 0) -> int:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    return default


class FormWizardWidget(Widget):
    def __init__(
        self,
        steps: list[FormWizardStep],
        label: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.steps = steps
        self.label = label
        self.cancelled = False

        values = self.message.metadata.get(FORM_VALUES_KEY, {})
        self.values = values if isinstance(values, dict) else {}
        self.step_index = _safe_index(self.message.metadata.get(FORM_STEP_INDEX_KEY))
        self.step_index = min(max(self.step_index, 0), len(self.steps))

        self._apply_input()
        self._apply_action()
        self._update_metadata()
        self.widget_message.body = self._build_body()

    @property
    def is_completed(self) -> bool:
        return self.step_index >= len(self.steps) and not self.cancelled

    @property
    def is_active(self) -> bool:
        return not self.cancelled and not self.is_completed

    def add_markup(self) -> None:
        if self.cancelled or self.is_completed:
            self.widget_bubbles.add_button(
                command=self.command,
                label="Сбросить",
                data={FORM_ACTION_KEY: FORM_ACTION_RESET},
            )
            self.add_additional_markup()
            return

        current_step = self.steps[self.step_index]
        if self.step_index > 0:
            self.widget_bubbles.add_button(
                command=self.command,
                label="Назад",
                data={FORM_ACTION_KEY: FORM_ACTION_BACK},
            )

        self.widget_bubbles.add_button(
            command=self.command,
            label="Далее",
            data={FORM_ACTION_KEY: FORM_ACTION_NEXT},
            new_row=self.step_index == 0,
        )
        self.widget_bubbles.add_button(
            command=self.command,
            label="Отмена",
            data={FORM_ACTION_KEY: FORM_ACTION_CANCEL},
            new_row=False,
        )
        self.widget_bubbles.add_button(
            command=self.command,
            label="Использовать текст сообщения",
            data={
                FORM_ACTION_KEY: FORM_ACTION_NEXT,
                FORM_INPUT_KEY: self.message.argument,
                "form_field": current_step.field,
            },
        )
        self.add_additional_markup()

    def _apply_input(self) -> None:
        if self.step_index >= len(self.steps):
            return

        if FORM_INPUT_KEY not in self.message.data:
            return

        current_step = self.steps[self.step_index]
        self.values[current_step.field] = str(self.message.data.get(FORM_INPUT_KEY, ""))

    def _apply_action(self) -> None:
        action = self.message.data.get(FORM_ACTION_KEY)
        if action == FORM_ACTION_BACK:
            self.step_index = max(self.step_index - 1, 0)
            return

        if action == FORM_ACTION_NEXT:
            self.step_index = min(self.step_index + 1, len(self.steps))
            return

        if action == FORM_ACTION_CANCEL:
            self.cancelled = True
            return

        if action == FORM_ACTION_RESET:
            self.cancelled = False
            self.step_index = 0
            self.values = {}

    def _update_metadata(self) -> None:
        self.widget_metadata[FORM_VALUES_KEY] = self.values
        self.widget_metadata[FORM_STEP_INDEX_KEY] = self.step_index
        self.widget_metadata["form_cancelled"] = self.cancelled

    def _build_body(self) -> str:
        if self.cancelled:
            return f"{self.label}\nОперация отменена."

        if self.is_completed:
            return f"{self.label}\nФорма заполнена."

        current_step = self.steps[self.step_index]
        current_value = self.values.get(current_step.field, "—")
        step_no = self.step_index + 1
        total = len(self.steps)
        return (
            f"{self.label}\n"
            f"Шаг {step_no}/{total}: {current_step.label}\n"
            f"Текущее значение: {current_value}"
        )

    @classmethod
    def get_values(cls, message: IncomingMessage) -> dict[str, Any]:
        values = message.metadata.get(FORM_VALUES_KEY, {})
        if not isinstance(values, dict):
            raise RuntimeError("Form values are not found in metadata.")
        return values
