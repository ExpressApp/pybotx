from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.select import SELECT_VALUE_KEY, SelectOption, SelectWidget


def _build_bot_mock() -> SimpleNamespace:
    return SimpleNamespace(send=AsyncMock(return_value=uuid4()), edit_message=AsyncMock())


@pytest.mark.asyncio
async def test__select_widget__display(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.data = {SELECT_VALUE_KEY: "b"}
    bot = _build_bot_mock()

    widget = SelectWidget(
        options=[
            "a",
            SelectOption(value="b", label="Bee"),
        ],
        label="Выберите",
        message=message,
        bot=bot,
        command="/select",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["a", "• Bee"]


def test__select_widget__get_value(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.data = {SELECT_VALUE_KEY: "value"}
    assert SelectWidget.get_value(message) == "value"

    message.data = {}
    with pytest.raises(RuntimeError):
        SelectWidget.get_value(message)
