from typing import Any

from pybotx.models.message.incoming_message import IncomingMessage

from .base import Widget

CONFIRM_ACTION_KEY = "confirm_action"
CONFIRM_ACTION = "confirm"
CANCEL_ACTION = "cancel"


class ConfirmWidget(Widget):
    def __init__(
        self,
        label: str,
        confirm_label: str = "Подтвердить",
        cancel_label: str = "Отмена",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.widget_message.body = label
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label

    def add_markup(self) -> None:
        self.widget_bubbles.add_button(
            command=self.command,
            label=self.confirm_label,
            data={CONFIRM_ACTION_KEY: CONFIRM_ACTION},
        )
        self.widget_bubbles.add_button(
            command=self.command,
            label=self.cancel_label,
            data={CONFIRM_ACTION_KEY: CANCEL_ACTION},
            new_row=False,
        )
        self.add_additional_markup()

    @classmethod
    def get_action(cls, message: IncomingMessage) -> str:
        action = message.data.get(CONFIRM_ACTION_KEY)
        if action not in {CONFIRM_ACTION, CANCEL_ACTION}:
            raise RuntimeError("Confirmation action is not found.")

        return str(action)

    @classmethod
    def is_confirmed(cls, message: IncomingMessage) -> bool:
        return cls.get_action(message) == CONFIRM_ACTION

    @classmethod
    def is_cancelled(cls, message: IncomingMessage) -> bool:
        return cls.get_action(message) == CANCEL_ACTION
