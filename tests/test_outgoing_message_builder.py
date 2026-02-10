from uuid import uuid4

import pytest

from pybotx.domain.message_builder import (
    EditMessageBuilder,
    OutgoingMessageBuilder,
    ReplyMessageBuilder,
)
from pybotx.domain.models.attachments import OutgoingAttachment
from pybotx.domain.models.message.markup import BubbleMarkup, KeyboardMarkup
from pybotx.domain.models.message.message_options import MessageOptions


def test__outgoing_message_builder__build() -> None:
    bot_id = uuid4()
    chat_id = uuid4()
    recipient_id = uuid4()

    bubbles = BubbleMarkup()
    bubbles.add_button(label="Bubble", command="/bubble")

    keyboard = KeyboardMarkup()
    keyboard.add_button(label="Keyboard", command="/keyboard")

    file = OutgoingAttachment(content=b"data", filename="file.txt")

    message = (
        OutgoingMessageBuilder(bot_id=bot_id, chat_id=chat_id, body="Hi!")
        .with_metadata({"foo": "bar"})
        .with_bubbles(bubbles)
        .with_keyboard(keyboard)
        .with_file(file)
        .to_recipients([recipient_id])
        .silent()
        .auto_adjust_buttons()
        .stealth()
        .no_push()
        .force_notification()
        .build()
    )

    assert message.bot_id == bot_id
    assert message.chat_id == chat_id
    assert message.body == "Hi!"
    assert message.metadata == {"foo": "bar"}
    assert message.bubbles == bubbles
    assert message.keyboard == keyboard
    assert message.file == file
    assert message.recipients == [recipient_id]
    assert message.silent_response is True
    assert message.markup_auto_adjust is True
    assert message.stealth_mode is True
    assert message.send_push is False
    assert message.ignore_mute is True


def test__outgoing_message_builder__with_options() -> None:
    bot_id = uuid4()
    chat_id = uuid4()
    recipients = [uuid4()]
    options = MessageOptions(
        recipients=recipients,
        silent_response=True,
        markup_auto_adjust=True,
        stealth_mode=True,
        send_push=False,
        ignore_mute=True,
    )

    message = (
        OutgoingMessageBuilder(bot_id=bot_id, chat_id=chat_id, body="Hi!")
        .with_options(options)
        .build()
    )

    assert message.recipients == recipients
    assert message.silent_response is True
    assert message.markup_auto_adjust is True
    assert message.stealth_mode is True
    assert message.send_push is False
    assert message.ignore_mute is True


def test__outgoing_message_builder__for_incoming(incoming_message_factory) -> None:
    incoming = incoming_message_factory()

    builder = OutgoingMessageBuilder.for_incoming(incoming, body="Hello")

    assert builder.bot_id == incoming.bot.id
    assert builder.chat_id == incoming.chat.id
    assert builder.body == "Hello"


def test__reply_message_builder__build() -> None:
    bot_id = uuid4()
    sync_id = uuid4()

    bubbles = BubbleMarkup()
    bubbles.add_button(label="Bubble", command="/bubble")

    keyboard = KeyboardMarkup()
    keyboard.add_button(label="Keyboard", command="/keyboard")

    file = OutgoingAttachment(content=b"data", filename="file.txt")

    message = (
        ReplyMessageBuilder(bot_id=bot_id, sync_id=sync_id, body="Hi!")
        .with_metadata({"foo": "bar"})
        .with_bubbles(bubbles)
        .with_keyboard(keyboard)
        .with_file(file)
        .silent()
        .auto_adjust_buttons()
        .stealth()
        .no_push()
        .force_notification()
        .build()
    )

    assert message.bot_id == bot_id
    assert message.sync_id == sync_id
    assert message.body == "Hi!"
    assert message.metadata == {"foo": "bar"}
    assert message.bubbles == bubbles
    assert message.keyboard == keyboard
    assert message.file == file
    assert message.silent_response is True
    assert message.markup_auto_adjust is True
    assert message.stealth_mode is True
    assert message.send_push is False
    assert message.ignore_mute is True


def test__reply_message_builder__with_options() -> None:
    bot_id = uuid4()
    sync_id = uuid4()
    options = MessageOptions(
        silent_response=True,
        markup_auto_adjust=True,
        stealth_mode=True,
        send_push=False,
        ignore_mute=True,
    )

    message = (
        ReplyMessageBuilder(bot_id=bot_id, sync_id=sync_id, body="Hi!")
        .with_options(options)
        .build()
    )

    assert message.silent_response is True
    assert message.markup_auto_adjust is True
    assert message.stealth_mode is True
    assert message.send_push is False
    assert message.ignore_mute is True


def test__reply_message_builder__for_incoming(incoming_message_factory) -> None:
    incoming = incoming_message_factory()
    sync_id = uuid4()

    builder = ReplyMessageBuilder.for_incoming(
        incoming,
        body="Reply",
        sync_id=sync_id,
    )

    assert builder.bot_id == incoming.bot.id
    assert builder.sync_id == sync_id
    assert builder.body == "Reply"


def test__reply_message_builder__for_incoming_message(incoming_message_factory) -> None:
    incoming = incoming_message_factory()

    builder = ReplyMessageBuilder.for_incoming_message(incoming, body="Reply")

    assert builder.bot_id == incoming.bot.id
    assert builder.sync_id == incoming.sync_id
    assert builder.body == "Reply"


def test__edit_message_builder__build() -> None:
    bot_id = uuid4()
    sync_id = uuid4()

    bubbles = BubbleMarkup()
    bubbles.add_button(label="Bubble", command="/bubble")

    keyboard = KeyboardMarkup()
    keyboard.add_button(label="Keyboard", command="/keyboard")

    file = OutgoingAttachment(content=b"data", filename="file.txt")

    message = (
        EditMessageBuilder(bot_id=bot_id, sync_id=sync_id)
        .with_body("Updated")
        .with_metadata({"foo": "bar"})
        .with_bubbles(bubbles)
        .with_keyboard(keyboard)
        .with_file(file)
        .auto_adjust_buttons()
        .build()
    )

    assert message.bot_id == bot_id
    assert message.sync_id == sync_id
    assert message.body == "Updated"
    assert message.metadata == {"foo": "bar"}
    assert message.bubbles == bubbles
    assert message.keyboard == keyboard
    assert message.file == file
    assert message.markup_auto_adjust is True


def test__edit_message_builder__clear_body_and_file() -> None:
    bot_id = uuid4()
    sync_id = uuid4()

    message = (
        EditMessageBuilder(bot_id=bot_id, sync_id=sync_id)
        .clear_body()
        .clear_file()
        .build()
    )

    assert message.body == ""
    assert message.file is None


def test__edit_message_builder__for_incoming_source(incoming_message_factory) -> None:
    incoming = incoming_message_factory()
    source_sync_id = uuid4()
    incoming.source_sync_id = source_sync_id

    builder = EditMessageBuilder.for_incoming_source(
        incoming,
        sync_id=source_sync_id,
    )

    assert builder.bot_id == incoming.bot.id
    assert builder.sync_id == source_sync_id


def test__edit_message_builder__for_incoming_source_id(incoming_message_factory) -> None:
    incoming = incoming_message_factory()
    source_sync_id = uuid4()
    incoming.source_sync_id = source_sync_id

    builder = EditMessageBuilder.for_incoming_source_id(incoming)

    assert builder.bot_id == incoming.bot.id
    assert builder.sync_id == source_sync_id


def test__edit_message_builder__for_incoming_source_id_missing_raises(
    incoming_message_factory,
) -> None:
    incoming = incoming_message_factory()

    with pytest.raises(ValueError, match="source_sync_id"):
        EditMessageBuilder.for_incoming_source_id(incoming)


def test__edit_message_builder__clear_metadata_bubbles_keyboard() -> None:
    bot_id = uuid4()
    sync_id = uuid4()

    message = (
        EditMessageBuilder(bot_id=bot_id, sync_id=sync_id)
        .clear_metadata()
        .clear_bubbles()
        .clear_keyboard()
        .build()
    )

    assert message.metadata == {}
    assert message.bubbles is None
    assert message.keyboard is None
