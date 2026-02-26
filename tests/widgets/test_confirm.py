from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.confirm import (
    CANCEL_ACTION,
    CONFIRM_ACTION,
    CONFIRM_ACTION_KEY,
    ConfirmWidget,
)


def _build_bot_mock() -> SimpleNamespace:
    return SimpleNamespace(send=AsyncMock(return_value=uuid4()), edit_message=AsyncMock())


@pytest.mark.asyncio
async def test__confirm_widget__display(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = ConfirmWidget(
        label="Подтвердите действие",
        message=message,
        bot=bot,
        command="/confirm",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    rows = [[button.label for button in row] for row in sent_message.bubbles]
    assert rows == [["Подтвердить", "Отмена"]]


def test__confirm_widget__actions(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.data = {CONFIRM_ACTION_KEY: CONFIRM_ACTION}

    assert ConfirmWidget.get_action(message) == CONFIRM_ACTION
    assert ConfirmWidget.is_confirmed(message)
    assert not ConfirmWidget.is_cancelled(message)

    message.data = {CONFIRM_ACTION_KEY: CANCEL_ACTION}
    assert ConfirmWidget.get_action(message) == CANCEL_ACTION
    assert ConfirmWidget.is_cancelled(message)

    message.data = {}
    with pytest.raises(RuntimeError):
        ConfirmWidget.get_action(message)
