from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.file_batch import (
    FILE_BATCH_ACTION_ITEM,
    FILE_BATCH_ACTION_KEY,
    FILE_BATCH_ACTION_NEXT,
    FILE_BATCH_FILE_NAME_KEY,
    FILE_BATCH_FILES_KEY,
    FILE_BATCH_PAGE_KEY,
    BatchFileItem,
    FileBatchWidget,
    _normalize_item,
    _safe_int,
    _status_icon,
)


def _build_bot_mock() -> Any:
    return SimpleNamespace(send=AsyncMock(return_value=uuid4()), edit_message=AsyncMock())


def test__file_batch_widget__helpers() -> None:
    assert _safe_int(1) == 1
    assert _safe_int("2") == 2
    assert _safe_int("bad") == 0

    assert _normalize_item(BatchFileItem(name="a", status="done")) is not None
    assert _normalize_item({"name": "b", "status": "failed"}) is not None
    assert _normalize_item("c") is not None
    assert _normalize_item({"name": "x"}) is None
    assert _normalize_item(1) is None

    assert _status_icon("done") == "✅"
    assert _status_icon("failed") == "❌"
    assert _status_icon("running") == "⏳"
    assert _status_icon("unknown") == "•"


@pytest.mark.asyncio
async def test__file_batch_widget__display(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {FILE_BATCH_PAGE_KEY: 0}
    bot = _build_bot_mock()

    widget = FileBatchWidget(
        files=[
            BatchFileItem(name="a.txt", status="done"),
            {"name": "b.txt", "status": "failed", "error": "oops"},
            "c.txt",
        ],
        page_size=2,
        message=message,
        bot=bot,
        command="/batch",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    assert "Всего: 3" in sent_message.body
    assert "Ошибок: 1" in sent_message.body
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["a.txt", "b.txt", "Вперед", "Повторить ошибки"]
    assert FILE_BATCH_FILES_KEY in sent_message.metadata


@pytest.mark.asyncio
async def test__file_batch_widget__metadata_source(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.metadata = {
        FILE_BATCH_FILES_KEY: [
            {"name": "x.txt", "status": "running"},
            {"name": "y.txt", "status": "done"},
        ],
        FILE_BATCH_PAGE_KEY: 1,
    }
    message.data = {FILE_BATCH_PAGE_KEY: 10}
    bot = _build_bot_mock()

    widget = FileBatchWidget(
        files=None,
        page_size=1,
        message=message,
        bot=bot,
        command="/batch",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["y.txt", "Назад"]

    message.metadata = {FILE_BATCH_FILES_KEY: "bad"}
    message.data = {}
    widget = FileBatchWidget(
        files=None,
        message=message,
        bot=bot,
        command="/batch",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert "Всего: 0" in sent_message.body


def test__file_batch_widget__getters(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {FILE_BATCH_ACTION_KEY: FILE_BATCH_ACTION_NEXT}
    assert FileBatchWidget.get_action(message) == FILE_BATCH_ACTION_NEXT

    message.data = {
        FILE_BATCH_ACTION_KEY: FILE_BATCH_ACTION_ITEM,
        FILE_BATCH_FILE_NAME_KEY: "a.txt",
    }
    assert FileBatchWidget.get_action(message) == FILE_BATCH_ACTION_ITEM
    assert FileBatchWidget.get_selected_file(message) == "a.txt"

    message.data = {}
    with pytest.raises(RuntimeError):
        FileBatchWidget.get_action(message)

    with pytest.raises(RuntimeError):
        FileBatchWidget.get_selected_file(message)
