from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.checklist import CHECKED_ITEMS_KEY, CheckListWidget, SELECTED_ITEM_KEY


def _build_bot_mock() -> SimpleNamespace:
    return SimpleNamespace(
        send=AsyncMock(return_value=uuid4()),
        edit_message=AsyncMock(),
    )


@pytest.mark.asyncio
async def test__checklist_widget__display(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.metadata = {CHECKED_ITEMS_KEY: ["b"]}
    bot = _build_bot_mock()

    widget = CheckListWidget(
        widget_content=["a", ["b", "c"]],
        label="Checklist",
        message=message,
        bot=bot,
        command="/checklist",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [[button.label for button in row] for row in sent_message.bubbles]

    assert sent_message.body == "Checklist"
    assert labels == [["☐ a"], ["☑ b", "☐ c"]]


@pytest.mark.asyncio
async def test__checklist_widget__toggle_selected_item(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.data = {SELECTED_ITEM_KEY: "x"}
    message.metadata = {CHECKED_ITEMS_KEY: ["x", "y"]}
    bot = _build_bot_mock()

    widget = CheckListWidget(
        widget_content=["x", "y"],
        label="Checklist",
        message=message,
        bot=bot,
        command="/checklist",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.metadata[CHECKED_ITEMS_KEY] == ["y"]


@pytest.mark.asyncio
async def test__checklist_widget__toggle_add_item(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.data = {SELECTED_ITEM_KEY: "z"}
    message.metadata = {CHECKED_ITEMS_KEY: ["x"]}
    bot = _build_bot_mock()

    widget = CheckListWidget(
        widget_content=["x", "z"],
        label="Checklist",
        message=message,
        bot=bot,
        command="/checklist",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.metadata[CHECKED_ITEMS_KEY] == ["x", "z"]


def test__checklist_widget__helpers(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.data = {SELECTED_ITEM_KEY: "test"}
    message.metadata = {CHECKED_ITEMS_KEY: ["a", "b"]}

    assert CheckListWidget.get_value(message) == "test"
    assert CheckListWidget.get_checked_items(message) == ["a", "b"]
