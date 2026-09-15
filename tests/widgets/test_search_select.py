from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.search_select import SEARCH_PAGE_KEY, SEARCH_QUERY_KEY, SearchSelectWidget


def _build_bot_mock() -> Any:
    return SimpleNamespace(send=AsyncMock(return_value=uuid4()), edit_message=AsyncMock())


@pytest.mark.asyncio
async def test__search_select_widget__display_without_query(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {SEARCH_PAGE_KEY: "1"}
    bot = _build_bot_mock()

    widget = SearchSelectWidget(
        options=["a", "b", "c", "d"],
        label="Поиск",
        page_size=2,
        message=message,
        bot=bot,
        command="/search",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["c", "d", "Назад"]


@pytest.mark.asyncio
async def test__search_select_widget__first_page_forward_only(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {SEARCH_PAGE_KEY: 0}
    bot = _build_bot_mock()

    widget = SearchSelectWidget(
        options=["a", "b", "c"],
        label="Поиск",
        page_size=1,
        message=message,
        bot=bot,
        command="/search",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["a", "Вперед"]


@pytest.mark.asyncio
async def test__search_select_widget__query_with_results(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {SEARCH_QUERY_KEY: "ap", SEARCH_PAGE_KEY: 100}
    bot = _build_bot_mock()

    widget = SearchSelectWidget(
        options=["apple", "banana", "apricot", "orange"],
        label="Поиск",
        page_size=1,
        message=message,
        bot=bot,
        command="/search",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    assert "Поиск: ap" in sent_message.body
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["apricot", "Назад"]


@pytest.mark.asyncio
async def test__search_select_widget__middle_page_controls(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {SEARCH_QUERY_KEY: "a", SEARCH_PAGE_KEY: 1}
    bot = _build_bot_mock()

    widget = SearchSelectWidget(
        options=["aa", "ab", "ac", "ad"],
        label="Поиск",
        page_size=1,
        message=message,
        bot=bot,
        command="/search",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["ab", "Назад", "Вперед"]


@pytest.mark.asyncio
async def test__search_select_widget__empty_result(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory(body="/search qwerty")
    bot = _build_bot_mock()

    widget = SearchSelectWidget(
        options=["apple", "banana"],
        label="Поиск",
        page_size=1,
        message=message,
        bot=bot,
        command="/search",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["Ничего не найдено"]
