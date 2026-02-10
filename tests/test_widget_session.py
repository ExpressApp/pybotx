from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from pybotx import (
    InMemoryWidgetStateStore,
    MultiMessageWidget,
    MultiWidgetState,
    SingleMessageWidget,
    SingleWidgetState,
    WidgetSession,
)
from pybotx.domain.errors import InvalidWidgetPayloadError
from pybotx.domain.models.message.edit_message import EditMessage
from pybotx.domain.models.message.incoming_message import IncomingMessage


class _DummyBot:
    def __init__(self, sync_ids: list[UUID]) -> None:
        self._sync_ids = list(sync_ids)
        self.sent_messages: list[object] = []
        self.edit_messages: list[object] = []

    async def send(self, *, message, wait_callback=True, callback_timeout=None):  # type: ignore[override]
        self.sent_messages.append(message)
        if not self._sync_ids:
            return uuid4()
        return self._sync_ids.pop(0)

    async def edit(self, *, message):  # type: ignore[override]
        self.edit_messages.append(message)


@pytest.mark.asyncio
async def test__widget_session__single_send_and_update(incoming_message_factory) -> None:
    widget = SingleMessageWidget(command="/demo")
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store, include_metadata=False)

    sync_id = uuid4()
    bot = _DummyBot([sync_id])

    await session.send_single(
        bot=bot,
        bot_id=uuid4(),
        chat_id=uuid4(),
        elems=["one", "two"],
        current_index=0,
    )

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {widget.index_key: 1}

    result = await session.update(bot=bot, message=incoming)

    assert result == [sync_id]
    assert [edit.body for edit in bot.edit_messages] == ["two"]


@pytest.mark.asyncio
async def test__widget_session__single_diff_skips_edit(incoming_message_factory) -> None:
    widget = SingleMessageWidget(command="/demo")
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store, include_metadata=False)

    sync_id = uuid4()
    bot = _DummyBot([sync_id])

    await store.set(sync_id, state=SingleWidgetState(elems=["one"], current_index=0))

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {widget.index_key: 0}

    result = await session.update(bot=bot, message=incoming, diff=True)

    assert result == []
    assert bot.edit_messages == []


@pytest.mark.asyncio
async def test__widget_session__multi_send_and_update(incoming_message_factory) -> None:
    widget = MultiMessageWidget(command="/demo", page_size=2)
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store, include_metadata=False)

    head_sync_id = uuid4()
    tail_sync_id = uuid4()
    bot = _DummyBot([head_sync_id, tail_sync_id])

    head_sync_ids, tail_id = await session.send_multi(
        bot=bot,
        bot_id=uuid4(),
        chat_id=uuid4(),
        elems=["a", "b", "c"],
        page=0,
    )

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = tail_id
    incoming.data = {widget.page_key: 1}

    result = await session.update(bot=bot, message=incoming, max_concurrency=2)

    assert tail_id == tail_sync_id
    assert head_sync_ids == [head_sync_id]
    assert len(result) == 2
    assert [edit.body for edit in bot.edit_messages] == ["c", widget.empty_text]


@pytest.mark.asyncio
async def test__widget_session__missing_state_raises(incoming_message_factory) -> None:
    widget = SingleMessageWidget(command="/demo")
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store)
    bot = _DummyBot([uuid4()])

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = uuid4()
    incoming.data = {widget.index_key: 0}

    with pytest.raises(InvalidWidgetPayloadError, match="state"):
        await session.update(bot=bot, message=incoming)


@pytest.mark.asyncio
async def test__widget_session__wrong_widget_type_send_single() -> None:
    widget = MultiMessageWidget(command="/demo", page_size=1)
    session = WidgetSession(widget=widget, store=InMemoryWidgetStateStore())

    with pytest.raises(InvalidWidgetPayloadError, match="single widgets"):
        await session.send_single(
            bot=_DummyBot([uuid4()]),
            bot_id=uuid4(),
            chat_id=uuid4(),
            elems=["x"],
        )


@pytest.mark.asyncio
async def test__widget_session__wrong_widget_type_send_multi() -> None:
    widget = SingleMessageWidget(command="/demo")
    session = WidgetSession(widget=widget, store=InMemoryWidgetStateStore())

    with pytest.raises(InvalidWidgetPayloadError, match="multi widgets"):
        await session.send_multi(
            bot=_DummyBot([uuid4()]),
            bot_id=uuid4(),
            chat_id=uuid4(),
            elems=["x"],
        )


@pytest.mark.asyncio
async def test__widget_session__update_without_source_sync_id(incoming_message_factory) -> None:
    widget = SingleMessageWidget(command="/demo")
    session = WidgetSession(widget=widget, store=InMemoryWidgetStateStore())

    incoming: IncomingMessage = incoming_message_factory()
    incoming.data = {widget.index_key: 0}

    with pytest.raises(InvalidWidgetPayloadError, match="source_sync_id"):
        await session.update(bot=_DummyBot([uuid4()]), message=incoming)


@pytest.mark.asyncio
async def test__widget_session__state_type_mismatch(incoming_message_factory) -> None:
    widget = SingleMessageWidget(command="/demo")
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store)
    sync_id = uuid4()

    await store.set(sync_id, state=MultiWidgetState(elems=["x"], page=0, sync_ids=[]))

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {widget.index_key: 0}

    with pytest.raises(InvalidWidgetPayloadError, match="type mismatch"):
        await session.update(bot=_DummyBot([uuid4()]), message=incoming)


@pytest.mark.asyncio
async def test__widget_session__update_missing_index_key(incoming_message_factory) -> None:
    widget = SingleMessageWidget(command="/demo")
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store)
    sync_id = uuid4()

    await store.set(sync_id, state=SingleWidgetState(elems=["x"], current_index=0))

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {}

    with pytest.raises(InvalidWidgetPayloadError, match="missing in data"):
        await session.update(bot=_DummyBot([uuid4()]), message=incoming)


@pytest.mark.asyncio
async def test__widget_session__update_missing_page_key(incoming_message_factory) -> None:
    widget = MultiMessageWidget(command="/demo", page_size=1)
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store)
    sync_id = uuid4()

    await store.set(sync_id, state=MultiWidgetState(elems=["x"], page=0, sync_ids=[]))

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {}

    with pytest.raises(InvalidWidgetPayloadError, match="missing in data"):
        await session.update(bot=_DummyBot([uuid4()]), message=incoming)


@pytest.mark.asyncio
async def test__widget_session__update_multi_diff_skip(incoming_message_factory) -> None:
    widget = MultiMessageWidget(command="/demo", page_size=1)
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store)
    sync_id = uuid4()

    await store.set(sync_id, state=MultiWidgetState(elems=["x"], page=0, sync_ids=[]))

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {widget.page_key: 0}

    result = await session.update(bot=_DummyBot([uuid4()]), message=incoming, diff=True)

    assert result == []


@pytest.mark.asyncio
async def test__widget_session__include_metadata_true() -> None:
    widget = SingleMessageWidget(command="/demo")
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store, include_metadata=True)
    sync_id = uuid4()
    bot = _DummyBot([sync_id])

    await session.send_single(
        bot=bot,
        bot_id=uuid4(),
        chat_id=uuid4(),
        elems=["x"],
        current_index=0,
    )

    sent_message = bot.sent_messages[0]
    assert sent_message.metadata


@pytest.mark.asyncio
async def test__widget_session__include_metadata_true_multi() -> None:
    widget = MultiMessageWidget(command="/demo", page_size=2)
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store, include_metadata=True)
    head_id = uuid4()
    tail_id = uuid4()
    bot = _DummyBot([head_id, tail_id])

    head_sync_ids, tail_sync_id = await session.send_multi(
        bot=bot,
        bot_id=uuid4(),
        chat_id=uuid4(),
        elems=["x", "y", "z"],
        page=0,
    )

    assert head_sync_ids == [head_id]
    assert tail_sync_id == tail_id
    assert bot.sent_messages[-1].metadata


@pytest.mark.asyncio
async def test__widget_session__parse_int_invalid_value(incoming_message_factory) -> None:
    widget = SingleMessageWidget(command="/demo")
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store)
    sync_id = uuid4()

    await store.set(sync_id, state=SingleWidgetState(elems=["x"], current_index=0))

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {widget.index_key: True}

    with pytest.raises(InvalidWidgetPayloadError, match="got bool"):
        await session.update(bot=_DummyBot([uuid4()]), message=incoming)


@pytest.mark.asyncio
async def test__widget_session__parse_int_invalid_str(incoming_message_factory) -> None:
    widget = MultiMessageWidget(command="/demo", page_size=1)
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store)
    sync_id = uuid4()

    await store.set(sync_id, state=MultiWidgetState(elems=["x"], page=0, sync_ids=[]))

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {widget.page_key: "nope"}

    with pytest.raises(InvalidWidgetPayloadError, match="integer string"):
        await session.update(bot=_DummyBot([uuid4()]), message=incoming)


@pytest.mark.asyncio
async def test__widget_session__apply_edits_empty() -> None:
    await WidgetSession._apply_edits(bot=_DummyBot([uuid4()]), edits=[], max_concurrency=None)


@pytest.mark.asyncio
async def test__widget_session__apply_edits_sequential() -> None:
    bot = _DummyBot([uuid4()])
    edits = [
        EditMessage(bot_id=uuid4(), sync_id=uuid4(), body="one"),
        EditMessage(bot_id=uuid4(), sync_id=uuid4(), body="two"),
    ]

    await WidgetSession._apply_edits(bot=bot, edits=edits, max_concurrency=1)

    assert [edit.body for edit in bot.edit_messages] == ["one", "two"]


@pytest.mark.asyncio
async def test__widget_session__parse_int_invalid_type(incoming_message_factory) -> None:
    widget = SingleMessageWidget(command="/demo")
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store)
    sync_id = uuid4()

    await store.set(sync_id, state=SingleWidgetState(elems=["x"], current_index=0))

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {widget.index_key: ["bad"]}

    with pytest.raises(InvalidWidgetPayloadError, match="must be an integer"):
        await session.update(bot=_DummyBot([uuid4()]), message=incoming)


@pytest.mark.asyncio
async def test__widget_session__state_type_mismatch_multi(incoming_message_factory) -> None:
    widget = MultiMessageWidget(command="/demo", page_size=1)
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store)
    sync_id = uuid4()

    await store.set(sync_id, state=SingleWidgetState(elems=["x"], current_index=0))

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {widget.page_key: 0}

    with pytest.raises(InvalidWidgetPayloadError, match="type mismatch"):
        await session.update(bot=_DummyBot([uuid4()]), message=incoming)


@pytest.mark.asyncio
async def test__widget_session__unsupported_widget_type(incoming_message_factory) -> None:
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=object(), store=store)  # type: ignore[arg-type]
    sync_id = uuid4()

    await store.set(sync_id, state=object())

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {"page": 0}

    with pytest.raises(InvalidWidgetPayloadError, match="Unsupported widget type"):
        await session.update(bot=_DummyBot([uuid4()]), message=incoming)


@pytest.mark.asyncio
async def test__widget_session__update_single_include_metadata(incoming_message_factory) -> None:
    widget = SingleMessageWidget(command="/demo")
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store, include_metadata=True)
    sync_id = uuid4()

    await store.set(sync_id, state=SingleWidgetState(elems=["x", "y"], current_index=0))

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {widget.index_key: 1}

    await session.update(bot=_DummyBot([uuid4()]), message=incoming)


@pytest.mark.asyncio
async def test__widget_session__update_multi_include_metadata(incoming_message_factory) -> None:
    widget = MultiMessageWidget(command="/demo", page_size=1)
    store = InMemoryWidgetStateStore()
    session = WidgetSession(widget=widget, store=store, include_metadata=True)
    sync_id = uuid4()

    await store.set(sync_id, state=MultiWidgetState(elems=["x", "y"], page=0, sync_ids=[]))

    incoming: IncomingMessage = incoming_message_factory()
    incoming.source_sync_id = sync_id
    incoming.data = {widget.page_key: 1}

    await session.update(bot=_DummyBot([uuid4()]), message=incoming, max_concurrency=1)
