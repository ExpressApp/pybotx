import asyncio
from uuid import UUID, uuid4

import pytest

from pybotx.application.bot_facets.widgets import BotWidgetsMixin
from pybotx.domain.widgets import MultiMessageWidget, SingleMessageWidget
from pybotx.infrastructure.widget_state_store import InMemoryWidgetStateStore


class DummyBot(BotWidgetsMixin):
    def __init__(self, sync_ids: list[UUID]) -> None:
        self._sync_ids = list(sync_ids)
        self.sent_messages = []
        self.edited_messages = []

    async def send(self, *, message, wait_callback=True, callback_timeout=None):
        self.sent_messages.append(message)
        return self._sync_ids.pop(0)

    async def edit(self, *, message) -> None:
        self.edited_messages.append(message)


def test__parse_optional_int__invalid_values() -> None:
    assert BotWidgetsMixin._parse_optional_int(True) is None
    assert BotWidgetsMixin._parse_optional_int("bad") is None
    assert BotWidgetsMixin._parse_optional_int(1.5) is None


async def test__send_single_widget() -> None:
    sync_id = uuid4()
    bot = DummyBot([sync_id])
    widget = SingleMessageWidget(command="/widget")

    result = await bot.send_single_widget(
        bot_id=uuid4(),
        chat_id=uuid4(),
        widget=widget,
        elems=["one", "two"],
        current_index=1,
    )

    assert result == sync_id
    assert bot.sent_messages[0].body == "two"


async def test__send_multi_widget() -> None:
    sync_ids = [uuid4(), uuid4(), uuid4()]
    bot = DummyBot(sync_ids)
    widget = MultiMessageWidget(command="/widget", page_size=3)

    result = await bot.send_multi_widget(
        bot_id=uuid4(),
        chat_id=uuid4(),
        widget=widget,
        elems=[1, 2, 3],
        page=0,
    )

    assert result.head_sync_ids == sync_ids[:2]
    assert result.tail_sync_id == sync_ids[2]
    tail_message = bot.sent_messages[-1]
    assert tail_message.metadata["sync_ids"] == [
        str(sync_ids[0]),
        str(sync_ids[1]),
    ]


async def test__update_widget__single(incoming_message_factory) -> None:
    bot = DummyBot([])
    widget = SingleMessageWidget(command="/widget")
    message = incoming_message_factory()
    message.data = {"current_index": "1"}
    message.metadata = {"elems": ["a", "b"]}
    message.source_sync_id = uuid4()

    updated_sync_ids = await bot.update_widget(widget=widget, message=message)

    assert updated_sync_ids == [message.source_sync_id]
    assert len(bot.edited_messages) == 1


async def test__update_widget__single__diff_skip(incoming_message_factory) -> None:
    bot = DummyBot([])
    widget = SingleMessageWidget(command="/widget")
    message = incoming_message_factory()
    message.data = {"current_index": "1"}
    message.metadata = {"elems": ["a", "b"], "current_index": 1}
    message.source_sync_id = uuid4()

    updated_sync_ids = await bot.update_widget(widget=widget, message=message)

    assert updated_sync_ids == []
    assert len(bot.edited_messages) == 0


async def test__update_widget__single__diff_no_skip(incoming_message_factory) -> None:
    bot = DummyBot([])
    widget = SingleMessageWidget(command="/widget")
    message = incoming_message_factory()
    message.data = {"current_index": "1"}
    message.metadata = {"elems": ["a", "b"], "current_index": 0}
    message.source_sync_id = uuid4()

    updated_sync_ids = await bot.update_widget(widget=widget, message=message)

    assert updated_sync_ids == [message.source_sync_id]
    assert len(bot.edited_messages) == 1


async def test__update_widget__single__diff_disabled(incoming_message_factory) -> None:
    bot = DummyBot([])
    widget = SingleMessageWidget(command="/widget")
    message = incoming_message_factory()
    message.data = {"current_index": "1"}
    message.metadata = {"elems": ["a", "b"], "current_index": 1}
    message.source_sync_id = uuid4()

    updated_sync_ids = await bot.update_widget(
        widget=widget,
        message=message,
        diff=False,
    )

    assert updated_sync_ids == [message.source_sync_id]
    assert len(bot.edited_messages) == 1


async def test__update_widget__multi(incoming_message_factory) -> None:
    bot = DummyBot([])
    widget = MultiMessageWidget(command="/widget", page_size=3)
    message = incoming_message_factory()
    sync_ids = [uuid4(), uuid4()]
    message.data = {"page": 1}
    message.metadata = {
        "elems": [1, 2, 3, 4, 5, 6],
        "sync_ids": [str(sync_ids[0]), str(sync_ids[1])],
    }
    message.source_sync_id = uuid4()

    updated_sync_ids = await bot.update_widget(widget=widget, message=message)

    assert updated_sync_ids == [sync_ids[0], sync_ids[1], message.source_sync_id]
    assert len(bot.edited_messages) == 3


async def test__update_widget__multi__diff_skip(incoming_message_factory) -> None:
    bot = DummyBot([])
    widget = MultiMessageWidget(command="/widget", page_size=3)
    message = incoming_message_factory()
    sync_ids = [uuid4(), uuid4()]
    message.data = {"page": 1}
    message.metadata = {
        "elems": [1, 2, 3, 4, 5, 6],
        "sync_ids": [str(sync_ids[0]), str(sync_ids[1])],
        "page": 1,
    }
    message.source_sync_id = uuid4()

    updated_sync_ids = await bot.update_widget(widget=widget, message=message)

    assert updated_sync_ids == []
    assert len(bot.edited_messages) == 0


async def test__update_widget__multi__diff_no_skip(incoming_message_factory) -> None:
    bot = DummyBot([])
    widget = MultiMessageWidget(command="/widget", page_size=3)
    message = incoming_message_factory()
    sync_ids = [uuid4(), uuid4()]
    message.data = {"page": 1}
    message.metadata = {
        "elems": [1, 2, 3, 4, 5, 6],
        "sync_ids": [str(sync_ids[0]), str(sync_ids[1])],
        "page": 0,
    }
    message.source_sync_id = uuid4()

    updated_sync_ids = await bot.update_widget(widget=widget, message=message)

    assert updated_sync_ids == [sync_ids[0], sync_ids[1], message.source_sync_id]
    assert len(bot.edited_messages) == 3


async def test__update_widget__multi__diff_disabled(incoming_message_factory) -> None:
    bot = DummyBot([])
    widget = MultiMessageWidget(command="/widget", page_size=3)
    message = incoming_message_factory()
    sync_ids = [uuid4(), uuid4()]
    message.data = {"page": 1}
    message.metadata = {
        "elems": [1, 2, 3, 4, 5, 6],
        "sync_ids": [str(sync_ids[0]), str(sync_ids[1])],
        "page": 1,
    }
    message.source_sync_id = uuid4()

    updated_sync_ids = await bot.update_widget(
        widget=widget,
        message=message,
        diff=False,
    )

    assert updated_sync_ids == [sync_ids[0], sync_ids[1], message.source_sync_id]
    assert len(bot.edited_messages) == 3


class ConcurrencyBot(BotWidgetsMixin):
    def __init__(self, expected_concurrency: int) -> None:
        self.current = 0
        self.max_seen = 0
        self.expected = expected_concurrency
        self.ready = asyncio.Event()
        self.start = asyncio.Event()

    async def edit(self, *, message) -> None:
        self.current += 1
        self.max_seen = max(self.max_seen, self.current)
        if self.current >= self.expected:
            self.ready.set()
        await self.start.wait()
        self.current -= 1


class ApplyEditsBot(BotWidgetsMixin):
    def __init__(self) -> None:
        self.calls = 0

    async def edit(self, *, message) -> None:
        self.calls += 1


async def test__update_widget__multi__concurrency_limit(incoming_message_factory) -> None:
    bot = ConcurrencyBot(expected_concurrency=2)
    widget = MultiMessageWidget(command="/widget", page_size=3)
    message = incoming_message_factory()
    sync_ids = [uuid4(), uuid4()]
    message.data = {"page": 1}
    message.metadata = {
        "elems": [1, 2, 3, 4, 5, 6],
        "sync_ids": [str(sync_ids[0]), str(sync_ids[1])],
    }
    message.source_sync_id = uuid4()

    task = asyncio.create_task(
        bot.update_widget(widget=widget, message=message, max_concurrency=2),
    )
    await bot.ready.wait()
    bot.start.set()
    await task

    assert bot.max_seen == 2


async def test__apply_edits__empty() -> None:
    bot = ApplyEditsBot()

    await bot._apply_edits(edits=[], max_concurrency=None)

    assert bot.calls == 0


class WidgetSessionBot(BotWidgetsMixin):
    def __init__(self, store=None) -> None:
        self._widget_state_store = store


def test__widget_session__uses_bot_store() -> None:
    store = InMemoryWidgetStateStore()
    bot = WidgetSessionBot(store)
    widget = SingleMessageWidget(command="/widget")

    session = bot.widget_session(widget=widget)

    assert session._store is store
    assert session._widget is widget


def test__widget_session__overrides_store() -> None:
    bot_store = InMemoryWidgetStateStore()
    override_store = InMemoryWidgetStateStore()
    bot = WidgetSessionBot(bot_store)
    widget = SingleMessageWidget(command="/widget")

    session = bot.widget_session(widget=widget, store=override_store)

    assert session._store is override_store


def test__widget_session__missing_store() -> None:
    bot = WidgetSessionBot()
    widget = SingleMessageWidget(command="/widget")

    with pytest.raises(ValueError, match="Widget state store is not configured"):
        bot.widget_session(widget=widget)


async def test__update_widget__invalid_type(incoming_message_factory) -> None:
    bot = DummyBot([])
    message = incoming_message_factory()

    with pytest.raises(TypeError):
        await bot.update_widget(widget=object(), message=message)
