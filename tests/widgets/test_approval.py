from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.approval import (
    APPROVAL_ACTION_KEY,
    APPROVE_ACTION,
    COMMENT_ACTION,
    REJECT_ACTION,
    ApprovalWidget,
)


def _build_bot_mock() -> Any:
    return SimpleNamespace(send=AsyncMock(return_value=uuid4()), edit_message=AsyncMock())


@pytest.mark.asyncio
async def test__approval_widget__display(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = ApprovalWidget(
        label="Согласовать заявку?",
        message=message,
        bot=bot,
        command="/approval",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    rows = [[button.label for button in row] for row in sent_message.bubbles]
    assert rows == [["Согласовать", "Отклонить"], ["Комментарий"]]


def test__approval_widget__actions(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {APPROVAL_ACTION_KEY: APPROVE_ACTION}
    assert ApprovalWidget.get_action(message) == APPROVE_ACTION
    assert ApprovalWidget.is_approved(message)

    message.data = {APPROVAL_ACTION_KEY: REJECT_ACTION}
    assert ApprovalWidget.get_action(message) == REJECT_ACTION

    message.data = {APPROVAL_ACTION_KEY: COMMENT_ACTION}
    assert ApprovalWidget.get_action(message) == COMMENT_ACTION

    message.data = {}
    with pytest.raises(RuntimeError):
        ApprovalWidget.get_action(message)
