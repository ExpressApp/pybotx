import uuid

import pytest
from pydantic import ValidationError

from botx import ChatMention, Mention, MentionTypes, UserMention


@pytest.mark.parametrize("mention_id", [None, uuid.uuid4()])
def test_mention_id_will_be_generated_if_missed(mention_id):
    mention = Mention(
        mention_id=mention_id, mention_data=UserMention(user_huid=uuid.uuid4()),
    )
    assert mention.mention_id is not None


@pytest.mark.parametrize(
    ("mention_data", "mention_type"),
    [
        (UserMention(user_huid=uuid.uuid4()), MentionTypes.user),
        (UserMention(user_huid=uuid.uuid4()), MentionTypes.contact),
        (ChatMention(group_chat_id=uuid.uuid4()), MentionTypes.chat),
        (ChatMention(group_chat_id=uuid.uuid4()), MentionTypes.channel),
    ],
)
def test_mention_corresponds_data_by_type(mention_data, mention_type) -> None:
    mention = Mention(mention_data=mention_data, mention_type=mention_type)
    assert mention.mention_type == mention_type


@pytest.mark.parametrize(
    ("mention_data", "mention_type"),
    [
        (UserMention(user_huid=uuid.uuid4()), MentionTypes.chat),
        (UserMention(user_huid=uuid.uuid4()), MentionTypes.channel),
        (ChatMention(group_chat_id=uuid.uuid4()), MentionTypes.user),
        (ChatMention(group_chat_id=uuid.uuid4()), MentionTypes.contact),
    ],
)
def test_error_when_data_not_corresponds_type(mention_data, mention_type) -> None:
    with pytest.raises(ValidationError):
        assert Mention(mention_data=mention_data, mention_type=mention_type)
