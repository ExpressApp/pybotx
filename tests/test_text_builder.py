from uuid import uuid4

from pybotx.domain.models.enums import MentionTypes
from pybotx.domain.text_builder import MentionComposer, TextBuilder


def test__text_builder__builds_text_with_mentions() -> None:
    user_id = uuid4()
    chat_id = uuid4()

    text = (
        TextBuilder()
        .append("Hello")
        .space()
        .mention_user(user_id, "Alice")
        .space()
        .append("from")
        .space()
        .mention_chat(chat_id, "Room")
        .build()
    )

    assert "<embed_mention>USER" in text
    assert "<embed_mention>CHAT" in text
    assert "Hello" in text


def test__text_builder__embed_raw() -> None:
    user_id = uuid4()

    text = TextBuilder().embed(mention_type=MentionTypes.USER, entity_id=user_id).build()

    assert text == f"<embed_mention>USER:{user_id}:</embed_mention>"


def test__mention_composer__is_text_builder() -> None:
    user_id = uuid4()

    text = MentionComposer().mention_user_named("Alice", user_id).build()

    assert "<embed_mention>USER" in text


def test__text_builder__named_mentions_and_join() -> None:
    user_id = uuid4()
    channel_id = uuid4()

    text = (
        TextBuilder()
        .join(["Hello", "world"], separator=" ", suffix=": ")
        .mention_user_named("Alice", user_id)
        .space()
        .mention_channel_named("News", channel_id)
        .build()
    )

    assert text.startswith("Hello world: ")
    assert "<embed_mention>USER" in text
    assert "<embed_mention>CHANNEL" in text


def test__text_builder__named_contact_and_chat() -> None:
    contact_id = uuid4()
    chat_id = uuid4()

    text = (
        TextBuilder()
        .mention_contact_named("Bob", contact_id)
        .space()
        .mention_chat_named("Room", chat_id)
        .build()
    )

    assert "<embed_mention>CONTACT" in text
    assert "<embed_mention>CHAT" in text


def test__text_builder__join_variants() -> None:
    builder = TextBuilder()
    builder.join([], separator=",")
    assert builder.build() == ""

    text = (
        TextBuilder()
        .join(["a", "b"], separator=",", prefix="[", suffix="]")
        .build()
    )

    assert text == "[a,b]"

    text_no_suffix = TextBuilder().join(["x", "y"], separator="-").build()
    assert text_no_suffix == "x-y"


def test__text_builder__newline_and_all_mentions() -> None:
    contact_id = uuid4()
    channel_id = uuid4()

    builder = (
        TextBuilder()
        .append("Line1")
        .newline()
        .mention_contact(contact_id, "Bob")
        .space()
        .mention_channel(channel_id, "News")
        .space()
        .mention_all()
    )

    text = str(builder)

    assert "Line1\n" in text
    assert "<embed_mention>CONTACT" in text
    assert "<embed_mention>CHANNEL" in text
    assert "<embed_mention>ALL" in text
