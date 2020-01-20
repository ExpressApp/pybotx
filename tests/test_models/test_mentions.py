import uuid

import pytest
from pydantic import ValidationError

from botx import ChatMention, Mention, MentionTypes, UserMention


def test_mention_id_will_be_generated_if_missed() -> None:
    assert (
        Mention(mention_data=UserMention(user_huid=uuid.uuid4())).mention_id is not None
    )


def test_mention_id_will_be_leaved_if_passed_to_init() -> None:
    mention_id = uuid.uuid4()
    assert (
        Mention(
            mention_id=mention_id, mention_data=UserMention(user_huid=uuid.uuid4())
        ).mention_id
        == mention_id
    )


def test_user_mention_is_user_mention_type() -> None:
    assert (
        Mention(mention_data=UserMention(user_huid=uuid.uuid4())).mention_type
        == MentionTypes.user
    )


def test_user_mention_is_contact_mention_type() -> None:
    assert (
        Mention(
            mention_data=UserMention(user_huid=uuid.uuid4()),
            mention_type=MentionTypes.contact,
        ).mention_type
        == MentionTypes.contact
    )


def test_user_mention_can_not_be_generated_with_chat_mention_type() -> None:
    with pytest.raises(ValidationError):
        assert Mention(
            mention_data=UserMention(user_huid=uuid.uuid4()),
            mention_type=MentionTypes.chat,
        )


def test_chat_mention_is_chat_mention_type() -> None:
    assert (
        Mention(
            mention_data=ChatMention(group_chat_id=uuid.uuid4()),
            mention_type=MentionTypes.chat,
        ).mention_type
        == MentionTypes.chat
    )


def test_chat_mention_can_not_be_generated_with_user_mention_type() -> None:
    with pytest.raises(ValidationError):
        assert Mention(
            mention_data=ChatMention(group_chat_id=uuid.uuid4()),
            mention_type=MentionTypes.user,
        )


def test_chat_mention_can_not_be_generated_with_contact_mention_type() -> None:
    with pytest.raises(ValidationError):
        assert Mention(
            mention_data=ChatMention(group_chat_id=uuid.uuid4()),
            mention_type=MentionTypes.contact,
        )
