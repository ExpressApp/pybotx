from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.base import PYBOTX_WIDGET_FLAG
from pybotx.widgets.range import CURRENT_INDEX_KEY, ELEMENTS_KEY, RangeWidget


def _build_bot_mock() -> Any:
    return SimpleNamespace(
        send=AsyncMock(return_value=uuid4()),
        edit_message=AsyncMock(),
    )


@pytest.mark.asyncio
async def test__range_widget__display_first_element(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = RangeWidget(
        elements=["1", "2", "3"],
        message=message,
        bot=bot,
        command="/range-widget",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    rows = [[button.label for button in row] for row in sent_message.bubbles]

    assert sent_message.body == "Current element: 1"
    assert sent_message.metadata[ELEMENTS_KEY] == ["1", "2", "3"]
    assert rows == [["Вперед"]]


@pytest.mark.asyncio
async def test__range_widget__display_middle_element(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {CURRENT_INDEX_KEY: 1}
    message.metadata = {PYBOTX_WIDGET_FLAG: 1, ELEMENTS_KEY: ["1", "2", "3"]}
    message.source_sync_id = uuid4()
    bot = _build_bot_mock()

    widget = RangeWidget(
        message=message,
        bot=bot,
        command="/range-widget",
    )
    await widget.display()

    assert bot.edit_message.await_count == 1
    edited_message_bubbles = bot.edit_message.await_args.kwargs["bubbles"]
    rows = [[button.label for button in row] for row in edited_message_bubbles]
    assert rows == [["Назад", "Вперед"]]


@pytest.mark.asyncio
async def test__range_widget__display_last_element(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {CURRENT_INDEX_KEY: 999}
    bot = _build_bot_mock()

    widget = RangeWidget(
        elements=["1", "2", "3"],
        message=message,
        bot=bot,
        command="/range-widget",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    rows = [[button.label for button in row] for row in sent_message.bubbles]
    assert sent_message.body == "Current element: 3"
    assert rows == [["Назад"]]


@pytest.mark.asyncio
async def test__range_widget__empty_list(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = RangeWidget(
        elements=[],
        message=message,
        bot=bot,
        command="/range-widget",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.body == "Список пуст"
    assert list(sent_message.bubbles) == []


@pytest.mark.asyncio
async def test__range_widget__invalid_elements_in_metadata(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.metadata = {ELEMENTS_KEY: "bad"}
    bot = _build_bot_mock()

    widget = RangeWidget(
        message=message,
        bot=bot,
        command="/range-widget",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.body == "Список пуст"


@pytest.mark.asyncio
async def test__range_widget__negative_index_is_clamped(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {CURRENT_INDEX_KEY: -10}
    bot = _build_bot_mock()

    widget = RangeWidget(
        elements=["a", "b"],
        message=message,
        bot=bot,
        command="/range-widget",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.body == "Current element: a"


def test__range_widget__helpers(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {CURRENT_INDEX_KEY: "1"}
    message.metadata = {ELEMENTS_KEY: ["x", "y"]}
    assert RangeWidget.get_value(message) == "y"

    message.data = {CURRENT_INDEX_KEY: -1}
    with pytest.raises(RuntimeError):
        RangeWidget.get_value(message)

    message.metadata = {ELEMENTS_KEY: "bad"}
    with pytest.raises(RuntimeError):
        RangeWidget.get_value(message)
