from __future__ import annotations

from uuid import uuid4

import pytest

from pybotx.application.bot_facets.events import BotEventsMixin
from pybotx.application.bot_facets.notifications import BotNotificationsMixin
from pybotx.domain.models.message.edit_message import EditMessage
from pybotx.domain.models.message.message_options import MessageOptions
from pybotx.domain.models.message.outgoing_message import OutgoingMessage
from pybotx.domain.models.message.reply_message import ReplyMessage


class _DummyApi:
    def __init__(self) -> None:
        self.sent: list[str] = []
        self.edited: list[str] = []
        self.sent_options: list[tuple[object, object]] = []
        self.reply_options: list[tuple[object, object]] = []

    async def send_message(  # type: ignore[override]
        self,
        *,
        bot_id,
        chat_id,
        body,
        metadata,
        bubbles,
        keyboard,
        file,
        silent_response,
        markup_auto_adjust,
        recipients,
        stealth_mode,
        send_push,
        ignore_mute,
        wait_callback,
        callback_timeout,
    ):
        self.sent.append(body)
        self.sent_options.append((silent_response, send_push))
        if body == "fail":
            raise RuntimeError("send failed")
        return uuid4()

    async def edit_message(  # type: ignore[override]
        self,
        *,
        bot_id,
        sync_id,
        body,
        metadata,
        bubbles,
        keyboard,
        file,
        markup_auto_adjust,
    ):
        self.edited.append(body if isinstance(body, str) else "")
        if body == "fail":
            raise RuntimeError("edit failed")

    async def reply_message(  # type: ignore[override]
        self,
        *,
        bot_id,
        sync_id,
        body,
        metadata,
        bubbles,
        keyboard,
        file,
        silent_response,
        markup_auto_adjust,
        stealth_mode,
        send_push,
        ignore_mute,
    ):
        self.reply_options.append((silent_response, send_push))
        if body == "fail":
            raise RuntimeError("reply failed")


class _DummyBot(BotNotificationsMixin, BotEventsMixin):
    def __init__(self) -> None:
        self._botx_api = _DummyApi()


@pytest.mark.asyncio
async def test__bulk_send__sequential_with_failures() -> None:
    bot = _DummyBot()
    messages = [
        OutgoingMessage(bot_id=uuid4(), chat_id=uuid4(), body="ok"),
        OutgoingMessage(bot_id=uuid4(), chat_id=uuid4(), body="fail"),
    ]

    result = await bot.bulk_send(messages=messages)

    assert len(result.items) == 2
    assert len(result.successes) == 1
    assert len(result.failures) == 1
    assert result.items[1].error is not None


@pytest.mark.asyncio
async def test__bulk_send__concurrent() -> None:
    bot = _DummyBot()
    messages = [
        OutgoingMessage(bot_id=uuid4(), chat_id=uuid4(), body="one"),
        OutgoingMessage(bot_id=uuid4(), chat_id=uuid4(), body="two"),
        OutgoingMessage(bot_id=uuid4(), chat_id=uuid4(), body="three"),
    ]

    result = await bot.bulk_send(messages=messages, max_concurrency=2)

    assert len(result.items) == 3
    assert len(result.successes) == 3
    assert [item.message.body for item in result.items] == ["one", "two", "three"]


@pytest.mark.asyncio
async def test__bulk_send__empty() -> None:
    bot = _DummyBot()

    result = await bot.bulk_send(messages=[])

    assert result.items == []


@pytest.mark.asyncio
async def test__bulk_send__concurrent_failure() -> None:
    bot = _DummyBot()
    messages = [
        OutgoingMessage(bot_id=uuid4(), chat_id=uuid4(), body="ok"),
        OutgoingMessage(bot_id=uuid4(), chat_id=uuid4(), body="fail"),
    ]

    result = await bot.bulk_send(messages=messages, max_concurrency=2)

    assert len(result.items) == 2
    assert len(result.failures) == 1
    assert result.items[1].error is not None


@pytest.mark.asyncio
async def test__bulk_send__options_applied() -> None:
    bot = _DummyBot()
    messages = [
        OutgoingMessage(bot_id=uuid4(), chat_id=uuid4(), body="one"),
        OutgoingMessage(
            bot_id=uuid4(),
            chat_id=uuid4(),
            body="two",
            silent_response=False,
        ),
    ]
    options = MessageOptions(silent_response=True, send_push=False)

    await bot.bulk_send(messages=messages, options=options)

    assert bot._botx_api.sent_options == [(True, False), (False, False)]


@pytest.mark.asyncio
async def test__bulk_edit__sequential_with_failures() -> None:
    bot = _DummyBot()
    messages = [
        EditMessage(bot_id=uuid4(), sync_id=uuid4(), body="ok"),
        EditMessage(bot_id=uuid4(), sync_id=uuid4(), body="fail"),
    ]

    result = await bot.bulk_edit(messages=messages)

    assert len(result.items) == 2
    assert len(result.successes) == 1
    assert len(result.failures) == 1
    assert result.items[1].error is not None


@pytest.mark.asyncio
async def test__bulk_edit__concurrent() -> None:
    bot = _DummyBot()
    messages = [
        EditMessage(bot_id=uuid4(), sync_id=uuid4(), body="one"),
        EditMessage(bot_id=uuid4(), sync_id=uuid4(), body="two"),
        EditMessage(bot_id=uuid4(), sync_id=uuid4(), body="three"),
    ]

    result = await bot.bulk_edit(messages=messages, max_concurrency=2)

    assert len(result.items) == 3
    assert len(result.successes) == 3
    assert [item.message.body for item in result.items] == ["one", "two", "three"]


@pytest.mark.asyncio
async def test__bulk_edit__empty() -> None:
    bot = _DummyBot()

    result = await bot.bulk_edit(messages=[])

    assert result.items == []


@pytest.mark.asyncio
async def test__bulk_edit__concurrent_failure() -> None:
    bot = _DummyBot()
    messages = [
        EditMessage(bot_id=uuid4(), sync_id=uuid4(), body="ok"),
        EditMessage(bot_id=uuid4(), sync_id=uuid4(), body="fail"),
    ]

    result = await bot.bulk_edit(messages=messages, max_concurrency=2)

    assert len(result.items) == 2
    assert len(result.failures) == 1
    assert result.items[1].error is not None


@pytest.mark.asyncio
async def test__bulk_reply__sequential_with_failures() -> None:
    bot = _DummyBot()
    messages = [
        ReplyMessage(bot_id=uuid4(), sync_id=uuid4(), body="ok"),
        ReplyMessage(bot_id=uuid4(), sync_id=uuid4(), body="fail"),
    ]

    result = await bot.bulk_reply(messages=messages)

    assert len(result.items) == 2
    assert len(result.successes) == 1
    assert len(result.failures) == 1
    assert result.items[1].error is not None


@pytest.mark.asyncio
async def test__bulk_reply__concurrent() -> None:
    bot = _DummyBot()
    messages = [
        ReplyMessage(bot_id=uuid4(), sync_id=uuid4(), body="one"),
        ReplyMessage(bot_id=uuid4(), sync_id=uuid4(), body="two"),
    ]

    result = await bot.bulk_reply(messages=messages, max_concurrency=2)

    assert len(result.items) == 2
    assert len(result.successes) == 2


@pytest.mark.asyncio
async def test__bulk_reply__concurrent_failure() -> None:
    bot = _DummyBot()
    messages = [
        ReplyMessage(bot_id=uuid4(), sync_id=uuid4(), body="ok"),
        ReplyMessage(bot_id=uuid4(), sync_id=uuid4(), body="fail"),
    ]

    result = await bot.bulk_reply(messages=messages, max_concurrency=2)

    assert len(result.items) == 2
    assert len(result.failures) == 1
    assert result.items[1].error is not None


@pytest.mark.asyncio
async def test__bulk_reply__empty() -> None:
    bot = _DummyBot()

    result = await bot.bulk_reply(messages=[])

    assert result.items == []


@pytest.mark.asyncio
async def test__bulk_reply__options_applied() -> None:
    bot = _DummyBot()
    messages = [
        ReplyMessage(bot_id=uuid4(), sync_id=uuid4(), body="one"),
        ReplyMessage(
            bot_id=uuid4(),
            sync_id=uuid4(),
            body="two",
            send_push=True,
        ),
    ]
    options = MessageOptions(silent_response=True, send_push=False)

    await bot.bulk_reply(messages=messages, options=options)

    assert bot._botx_api.reply_options == [(True, False), (True, True)]
