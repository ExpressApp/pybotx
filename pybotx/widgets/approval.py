from typing import Any

from pybotx.models.message.incoming_message import IncomingMessage

from .base import Widget

APPROVAL_ACTION_KEY = "approval_action"
APPROVE_ACTION = "approve"
REJECT_ACTION = "reject"
COMMENT_ACTION = "comment"


class ApprovalWidget(Widget):
    def __init__(
        self,
        label: str,
        approve_label: str = "Согласовать",
        reject_label: str = "Отклонить",
        comment_label: str = "Комментарий",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.widget_message.body = label
        self.approve_label = approve_label
        self.reject_label = reject_label
        self.comment_label = comment_label

    def add_markup(self) -> None:
        self.widget_bubbles.add_button(
            command=self.command,
            label=self.approve_label,
            data={APPROVAL_ACTION_KEY: APPROVE_ACTION},
        )
        self.widget_bubbles.add_button(
            command=self.command,
            label=self.reject_label,
            data={APPROVAL_ACTION_KEY: REJECT_ACTION},
            new_row=False,
        )
        self.widget_bubbles.add_button(
            command=self.command,
            label=self.comment_label,
            data={APPROVAL_ACTION_KEY: COMMENT_ACTION},
        )
        self.add_additional_markup()

    @classmethod
    def get_action(cls, message: IncomingMessage) -> str:
        action = message.data.get(APPROVAL_ACTION_KEY)
        if action not in {APPROVE_ACTION, REJECT_ACTION, COMMENT_ACTION}:
            raise RuntimeError("Approval action is not found.")

        return str(action)

    @classmethod
    def is_approved(cls, message: IncomingMessage) -> bool:
        return cls.get_action(message) == APPROVE_ACTION
