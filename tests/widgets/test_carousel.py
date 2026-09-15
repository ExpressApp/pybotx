from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.base import PYBOTX_WIDGET_FLAG
from pybotx.widgets.carousel import (
    LEFT_PRESSED,
    MESSAGE_LABEL_KEY,
    RIGHT_PRESSED,
    SELECTED_VALUE_KEY,
    SELECTED_VALUE_LABEL_KEY,
    START_FROM_KEY,
    CarouselWidget,
    _to_int,
)


def _build_bot_mock() -> Any:
    return SimpleNamespace(
        send=AsyncMock(return_value=uuid4()),
        edit_message=AsyncMock(),
    )


@pytest.mark.asyncio
async def test__carousel_widget__display_inline(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = CarouselWidget(
        widget_content=["a", "b", "c", "d"],
        label="Carousel",
        start_from=0,
        displayed_content_count=2,
        loop=False,
        inline=True,
        message=message,
        bot=bot,
        command="/carousel",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["a", "b", "➡️"]


@pytest.mark.asyncio
async def test__carousel_widget__display_newline(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {SELECTED_VALUE_KEY: RIGHT_PRESSED, START_FROM_KEY: 0}
    bot = _build_bot_mock()

    widget = CarouselWidget(
        widget_content=[["a", "b"], "c", "d"],
        label="Carousel",
        displayed_content_count=2,
        inline=False,
        loop=False,
        message=message,
        bot=bot,
        command="/carousel",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [[button.label for button in row] for row in sent_message.bubbles]
    assert labels == [["d"], ["⬅️"]]


@pytest.mark.asyncio
async def test__carousel_widget__get_value_selected(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.source_sync_id = uuid4()
    message.metadata = {PYBOTX_WIDGET_FLAG: 1}
    message.data = {
        SELECTED_VALUE_KEY: "value",
        MESSAGE_LABEL_KEY: "Label:",
        SELECTED_VALUE_LABEL_KEY: "{label} {selected_val}",
        START_FROM_KEY: 1,
    }
    bot = _build_bot_mock()

    selected_value = await CarouselWidget.get_value(message, bot)

    assert selected_value == "value"
    assert bot.edit_message.await_count == 1
    assert SELECTED_VALUE_KEY not in message.data


@pytest.mark.asyncio
async def test__carousel_widget__get_value_selected_without_feedback(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.source_sync_id = uuid4()
    message.metadata = {PYBOTX_WIDGET_FLAG: 1}
    message.data = {
        SELECTED_VALUE_KEY: "value",
        MESSAGE_LABEL_KEY: "Label:",
        SELECTED_VALUE_LABEL_KEY: "{label} {selected_val}",
        START_FROM_KEY: 1,
    }
    bot = _build_bot_mock()

    selected_value = await CarouselWidget.get_value(
        message,
        bot,
        send_feedback=False,
    )

    assert selected_value == "value"
    assert bot.edit_message.await_count == 0
    assert bot.send.await_count == 0
    assert SELECTED_VALUE_KEY not in message.data


@pytest.mark.asyncio
async def test__carousel_widget__get_value_empty(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {SELECTED_VALUE_KEY: LEFT_PRESSED}
    bot = _build_bot_mock()

    selected_value = await CarouselWidget.get_value(message, bot)

    assert selected_value is None


def test__carousel_widget__helpers(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    assert _to_int(10, 1) == 10
    assert _to_int("7", 1) == 7
    assert _to_int("x", 1) == 1

    widget = CarouselWidget(
        widget_content=[],
        label="Carousel",
        message=message,
        bot=bot,
        command="/carousel",
    )
    assert widget.start_from == 0


def test__carousel_widget__visibility_and_labels(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = CarouselWidget(
        widget_content=["a", "b", "c"],
        label="Carousel",
        displayed_content_count=1,
        show_numbers=True,
        loop=False,
        inline=False,
        message=message,
        bot=bot,
        command="/carousel",
    )
    widget._start_from = 5
    assert widget.start_from == 2
    assert widget.left_btn_label == "⬅️ (2-2)"
    assert widget.right_btn_label == "➡️ (4-3)"

    widget.loop = True
    assert list(widget.displayed_content) == ["c"]
    assert widget.get_left_and_right_button_visibility() == (True, True)

    short_widget = CarouselWidget(
        widget_content=["x"],
        label="Short",
        displayed_content_count=2,
        loop=False,
        inline=True,
        message=message,
        bot=bot,
        command="/carousel",
    )
    assert short_widget.get_left_and_right_button_visibility() == (False, False)

    wide_widget = CarouselWidget(
        widget_content=["a", "b", "c", "d", "e", "f", "g"],
        label="Wide",
        displayed_content_count=1,
        show_numbers=True,
        loop=False,
        inline=False,
        message=message,
        bot=bot,
        command="/carousel",
    )
    wide_widget._start_from = 1
    assert wide_widget.right_btn_label == "➡️ (3-3)"


@pytest.mark.asyncio
async def test__carousel_widget__inline_all_buttons_visible(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {SELECTED_VALUE_KEY: LEFT_PRESSED, START_FROM_KEY: 1}
    bot = _build_bot_mock()

    widget = CarouselWidget(
        widget_content=["a", "b", "c", "d"],
        label="Carousel",
        displayed_content_count=2,
        loop=False,
        inline=True,
        message=message,
        bot=bot,
        command="/carousel",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["⬅️", "d"]


@pytest.mark.asyncio
async def test__carousel_widget__newline_with_row_and_right_arrow(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = CarouselWidget(
        widget_content=[["a", "b"], "c", "d", "e"],
        label="Carousel",
        displayed_content_count=2,
        loop=False,
        inline=False,
        message=message,
        bot=bot,
        command="/carousel",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [[button.label for button in row] for row in sent_message.bubbles]
    assert labels == [["a", "b"], ["c"], ["➡️"]]


def test__carousel_widget__invalid_selected_value_label(
    incoming_message_factory: Any,
) -> None:
    class _BadCarousel(CarouselWidget):
        SELECTED_VALUE_LABEL = "{label}"

    message = incoming_message_factory()
    bot = _build_bot_mock()

    with pytest.raises(ValueError):
        _BadCarousel(
            widget_content=["a"],
            label="Carousel",
            message=message,
            bot=bot,
            command="/carousel",
        )


def test__carousel_widget__validation_errors(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    with pytest.raises(ValueError):
        CarouselWidget(
            widget_content=["a"],
            label="Carousel",
            start_from=2,
            message=message,
            bot=bot,
            command="/carousel",
        )

    with pytest.raises(ValueError):
        CarouselWidget(
            widget_content=["a"],
            label="Carousel",
            displayed_content_count=0,
            message=message,
            bot=bot,
            command="/carousel",
        )

    with pytest.raises(ValueError):
        CarouselWidget(
            widget_content=["a", "b"],
            label="Carousel",
            show_numbers=True,
            loop=True,
            inline=False,
            message=message,
            bot=bot,
            command="/carousel",
        )

    with pytest.raises(ValueError):
        CarouselWidget(
            widget_content=["a", "b"],
            label="Carousel",
            show_numbers=True,
            loop=False,
            inline=True,
            message=message,
            bot=bot,
            command="/carousel",
        )

    with pytest.raises(ValueError):
        CarouselWidget(
            widget_content=["a", "b"],
            label="Carousel",
            show_numbers=True,
            loop=False,
            inline=False,
            control_labels=("{bad}", "{}-{}"),
            message=message,
            bot=bot,
            command="/carousel",
        )

    with pytest.raises(ValueError):
        CarouselWidget(
            widget_content=["a", "b"],
            label="Carousel",
            show_numbers=True,
            loop=False,
            inline=False,
            control_labels=("{}-{}", "{}"),
            message=message,
            bot=bot,
            command="/carousel",
        )
