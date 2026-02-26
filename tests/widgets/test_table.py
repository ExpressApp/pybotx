from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.table import (
    TABLE_DESC_KEY,
    TABLE_PAGE_KEY,
    TABLE_QUERY_KEY,
    TABLE_SORT_KEY,
    TableWidget,
    _safe_bool,
    _safe_int,
)


def _build_bot_mock() -> SimpleNamespace:
    return SimpleNamespace(send=AsyncMock(return_value=uuid4()), edit_message=AsyncMock())


def test__table_widget__helpers() -> None:
    assert _safe_int(1) == 1
    assert _safe_int("2") == 2
    assert _safe_int("bad") == 0

    assert _safe_bool(True)
    assert _safe_bool("true")
    assert _safe_bool("1")
    assert not _safe_bool("no")
    assert not _safe_bool(None)


@pytest.mark.asyncio
async def test__table_widget__display(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.data = {
        TABLE_QUERY_KEY: "a",
        TABLE_SORT_KEY: "name",
        TABLE_DESC_KEY: "true",
        TABLE_PAGE_KEY: 0,
    }
    bot = _build_bot_mock()

    widget = TableWidget(
        rows=[
            {"name": "Alice", "role": "admin"},
            {"name": "Bob", "role": "user"},
            {"name": "Charlie", "role": "admin"},
        ],
        columns=["name", "role"],
        label="Пользователи",
        page_size=1,
        message=message,
        bot=bot,
        command="/table",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    assert "Пользователи" in sent_message.body
    assert "Фильтр: a" in sent_message.body
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["Вперед", "Сорт: name", "Сорт: role", "Сбросить фильтр"]


@pytest.mark.asyncio
async def test__table_widget__pagination_and_no_data(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.data = {TABLE_PAGE_KEY: 5}
    bot = _build_bot_mock()

    widget = TableWidget(
        rows=[{"name": "A"}, {"name": "B"}],
        columns=["name"],
        page_size=1,
        message=message,
        bot=bot,
        command="/table",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["Назад", "Сорт: name"]

    message = incoming_message_factory()
    widget = TableWidget(
        rows=[],
        columns=["name"],
        message=message,
        bot=bot,
        command="/table",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert "Нет данных" in sent_message.body


@pytest.mark.asyncio
async def test__table_widget__without_sort_column(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = TableWidget(
        rows=[{"name": "A"}],
        columns=[],
        message=message,
        bot=bot,
        command="/table",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.body.startswith("Таблица")
