from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from pybotx.widgets.base import (
    PYBOTX_WIDGET_FLAG,
    build_outgoing_message_from_incoming,
    ensure_widget_metadata,
)
from pybotx.widgets.pagination import (
    MESSAGE_IDS_KEY,
    START_FROM_KEY,
    PaginationWidget,
    _pagination_label,
    _safe_int,
    _to_uuid_list,
)


def _build_bot_mock() -> Any:
    message_ids = [
        UUID("00000000-0000-0000-0000-000000000001"),
        UUID("00000000-0000-0000-0000-000000000002"),
        UUID("00000000-0000-0000-0000-000000000003"),
    ]
    return SimpleNamespace(
        send=AsyncMock(side_effect=message_ids),
        edit_message=AsyncMock(),
    )


@pytest.mark.asyncio
async def test__pagination_widget__display_send(
    incoming_message_factory: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pybotx.widgets.pagination.asyncio.sleep", AsyncMock())
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = PaginationWidget(
        widget_content=["1", "2", "3"],
        paginate_by=2,
        message=message,
        bot=bot,
        command="/pagination",
    )
    await widget.display()

    assert bot.send.await_count == 2
    last_message = bot.send.await_args_list[-1].kwargs["message"]
    assert last_message.metadata[PYBOTX_WIDGET_FLAG] == 1
    assert "pagination_message_ids" in last_message.metadata


@pytest.mark.asyncio
async def test__pagination_widget__display_update(
    incoming_message_factory: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pybotx.widgets.pagination.asyncio.sleep", AsyncMock())

    message = incoming_message_factory()
    message.data = {"pagination_start_from": 1}
    message.metadata = {
        "pagination_message_ids": [
            "00000000-0000-0000-0000-000000000011",
            "00000000-0000-0000-0000-000000000012",
            "invalid",
        ],
        PYBOTX_WIDGET_FLAG: 1,
    }
    message.source_sync_id = uuid4()
    bot = _build_bot_mock()

    widget = PaginationWidget(
        widget_content=["1", "2", "3"],
        paginate_by=2,
        message=message,
        bot=bot,
        command="/pagination",
    )
    await widget.display()

    assert bot.edit_message.await_count >= 1


@pytest.mark.asyncio
async def test__pagination_widget__update_without_source_sync_id(
    incoming_message_factory: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pybotx.widgets.pagination.asyncio.sleep", AsyncMock())

    message = incoming_message_factory()
    message.data = {"pagination_start_from": 0}
    message.metadata = {
        "pagination_message_ids": ["00000000-0000-0000-0000-000000000021"],
    }
    message.source_sync_id = None
    bot = _build_bot_mock()

    widget = PaginationWidget(
        widget_content=["1", "2"],
        paginate_by=2,
        message=message,
        bot=bot,
        command="/pagination",
    )
    await widget.display()

    assert bot.send.await_count == 1


@pytest.mark.asyncio
async def test__pagination_widget__update_with_short_page(
    incoming_message_factory: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pybotx.widgets.pagination.asyncio.sleep", AsyncMock())

    message = incoming_message_factory()
    message.data = {START_FROM_KEY: 2}
    message.metadata = {
        MESSAGE_IDS_KEY: [
            "00000000-0000-0000-0000-000000000031",
            "00000000-0000-0000-0000-000000000032",
        ],
        PYBOTX_WIDGET_FLAG: 1,
    }
    message.source_sync_id = uuid4()
    bot = _build_bot_mock()

    widget = PaginationWidget(
        widget_content=["1", "2", "3"],
        paginate_by=3,
        message=message,
        bot=bot,
        command="/pagination",
    )
    await widget.display()

    assert bot.edit_message.await_count >= 2


@pytest.mark.asyncio
async def test__pagination_widget__update_break_on_missing_message_ids(
    incoming_message_factory: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pybotx.widgets.pagination.asyncio.sleep", AsyncMock())

    message = incoming_message_factory()
    message.data = {START_FROM_KEY: 1}
    message.metadata = {MESSAGE_IDS_KEY: ["00000000-0000-0000-0000-000000000041"]}
    message.source_sync_id = uuid4()
    bot = _build_bot_mock()

    widget = PaginationWidget(
        widget_content=["1", "2", "3"],
        paginate_by=3,
        message=message,
        bot=bot,
        command="/pagination",
    )
    await widget.display()

    assert bot.edit_message.await_count >= 1


@pytest.mark.asyncio
async def test__pagination_widget__empty_content(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = PaginationWidget(
        widget_content=[],
        paginate_by=2,
        message=message,
        bot=bot,
        command="/pagination",
    )
    await widget.display()

    assert bot.send.await_count == 0
    assert bot.edit_message.await_count == 0


def test__pagination_widget__validation_errors(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    with pytest.raises(ValueError):
        PaginationWidget(
            widget_content=["1"],
            paginate_by=0,
            message=message,
            bot=bot,
            command="/pagination",
        )

    with pytest.raises(ValueError):
        PaginationWidget(
            widget_content=["1"],
            paginate_by=1,
            delay_between_messages=-1,
            message=message,
            bot=bot,
            command="/pagination",
        )


def test__pagination_widget__normalize_outgoing_message(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    content_message = build_outgoing_message_from_incoming(
        message=message,
        body="original",
        metadata={"timestamp": datetime.now(timezone.utc).isoformat()},
    )

    widget = PaginationWidget(
        widget_content=[content_message],
        paginate_by=1,
        message=message,
        bot=bot,
        command="/pagination",
    )

    assert widget.widget_content[0].body == "original"
    assert widget.widget_content[0].bot_id == message.bot.id


def test__pagination_widget__helpers() -> None:
    assert _pagination_label(1, 1, backward=True) == "⬅️ Назад к [1]"
    assert _pagination_label(1, 3, backward=False) == "➡️ Вперёд к [1-3]"
    assert _safe_int(2, 0) == 2
    assert _safe_int("7", 0) == 7
    assert _safe_int("x", 9) == 9
    assert _to_uuid_list("bad") == []
    assert _to_uuid_list(["bad"]) == []


def test__pagination_widget__add_navigation_buttons(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {START_FROM_KEY: 2}
    bot = _build_bot_mock()

    widget = PaginationWidget(
        widget_content=["1", "2", "3", "4"],
        paginate_by=2,
        message=message,
        bot=bot,
        command="/pagination",
    )
    widget.add_markup()

    labels = [button.label for row in widget.widget_bubbles for button in row]
    assert labels == ["⬅️ Назад к [1-2]"]


def test__pagination_widget__negative_start_from(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.data = {START_FROM_KEY: -10}
    bot = _build_bot_mock()

    widget = PaginationWidget(
        widget_content=["1", "2", "3"],
        paginate_by=1,
        message=message,
        bot=bot,
        command="/pagination",
    )

    assert widget.start_from == 0


def test__pagination_widget__prepare_last_message_keeps_metadata(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = PaginationWidget(
        widget_content=["1"],
        paginate_by=1,
        message=message,
        bot=bot,
        command="/pagination",
    )
    widget.message_ids = [uuid4()]
    content_message = build_outgoing_message_from_incoming(
        message=message,
        body="body",
        metadata={"foo": "bar"},
    )

    widget._prepare_last_message(content_message)

    metadata = ensure_widget_metadata(content_message)
    assert metadata["foo"] == "bar"
    assert metadata[PYBOTX_WIDGET_FLAG] == 1
    assert MESSAGE_IDS_KEY in metadata
