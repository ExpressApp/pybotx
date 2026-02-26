from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.multi_select import (
    MULTI_SELECTED_VALUES_KEY,
    MULTI_SELECT_VALUE_KEY,
    MultiSelectWidget,
)


def _build_bot_mock() -> SimpleNamespace:
    return SimpleNamespace(send=AsyncMock(return_value=uuid4()), edit_message=AsyncMock())


@pytest.mark.asyncio
async def test__multi_select_widget__toggle(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.metadata = {MULTI_SELECTED_VALUES_KEY: ["a"]}
    message.data = {MULTI_SELECT_VALUE_KEY: "b"}
    bot = _build_bot_mock()

    widget = MultiSelectWidget(
        options=["a", "b"],
        label="Выберите",
        message=message,
        bot=bot,
        command="/multi-select",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.metadata[MULTI_SELECTED_VALUES_KEY] == ["a", "b"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["☑ a", "☑ b"]


@pytest.mark.asyncio
async def test__multi_select_widget__remove_and_limit(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.metadata = {MULTI_SELECTED_VALUES_KEY: ["a"]}
    message.data = {MULTI_SELECT_VALUE_KEY: "a"}
    bot = _build_bot_mock()

    widget = MultiSelectWidget(
        options=["a", "b"],
        label="Выберите",
        max_selected=1,
        message=message,
        bot=bot,
        command="/multi-select",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.metadata[MULTI_SELECTED_VALUES_KEY] == []

    message.data = {MULTI_SELECT_VALUE_KEY: "b"}
    message.metadata = {MULTI_SELECTED_VALUES_KEY: ["a"]}
    widget = MultiSelectWidget(
        options=["a", "b"],
        label="Выберите",
        max_selected=1,
        message=message,
        bot=bot,
        command="/multi-select",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.metadata[MULTI_SELECTED_VALUES_KEY] == ["a"]


def test__multi_select_widget__get_selected_values(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.metadata = {MULTI_SELECTED_VALUES_KEY: [1, "2"]}
    assert MultiSelectWidget.get_selected_values(message) == ["1", "2"]

    message.metadata = {MULTI_SELECTED_VALUES_KEY: "bad"}
    assert MultiSelectWidget.get_selected_values(message) == []


@pytest.mark.asyncio
async def test__multi_select_widget__without_clicked_value(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.metadata = {MULTI_SELECTED_VALUES_KEY: ["a"]}
    message.data = {}
    bot = _build_bot_mock()

    widget = MultiSelectWidget(
        options=["a", "b"],
        label="Выберите",
        message=message,
        bot=bot,
        command="/multi-select",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.metadata[MULTI_SELECTED_VALUES_KEY] == ["a"]
