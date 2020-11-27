import uuid

import pytest
from pydantic import ValidationError

from botx import (
    ChatMention,
    Mention,
    MentionTypes,
    Message,
    MessageBuilder,
    UserMention,
)


class TestMentions:
    @pytest.mark.parametrize("mention_id", [None, uuid.uuid4()])
    def test_mention_id_will_be_generated_if_missed(self, mention_id):
        mention = Mention(
            mention_id=mention_id, mention_data=UserMention(user_huid=uuid.uuid4()),
        )
        assert mention.mention_id is not None

    def test_error_when_no_mention_data(self):
        with pytest.raises(ValidationError):
            Mention(mention_type=MentionTypes.user)

    @pytest.mark.parametrize(
        ("mention_data", "mention_type"),
        [
            (UserMention(user_huid=uuid.uuid4()), MentionTypes.user),
            (UserMention(user_huid=uuid.uuid4()), MentionTypes.contact),
            (ChatMention(group_chat_id=uuid.uuid4()), MentionTypes.chat),
            (ChatMention(group_chat_id=uuid.uuid4()), MentionTypes.channel),
        ],
    )
    def test_mention_corresponds_data_by_type(self, mention_data, mention_type) -> None:
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
    def test_error_when_data_not_corresponds_type(
        self, mention_data, mention_type,
    ) -> None:
        with pytest.raises(ValidationError):
            assert Mention(mention_data=mention_data, mention_type=mention_type)

    @pytest.mark.parametrize(
        ("mention_data", "mention_type"),
        [
            (UserMention(user_huid=uuid.uuid4()), MentionTypes.user),
            (UserMention(user_huid=uuid.uuid4()), MentionTypes.contact),
            (ChatMention(group_chat_id=uuid.uuid4()), MentionTypes.chat),
            (ChatMention(group_chat_id=uuid.uuid4()), MentionTypes.channel),
        ],
    )
    def test_mention_in_message(self, mention_data, mention_type) -> None:
        builder = MessageBuilder()
        builder.mention(
            mention=Mention(mention_data=mention_data, mention_type=mention_type),
        )
        assert builder.message.entities.mentions[0]

    def test_mention_not_in_message(self, bot) -> None:
        builder = MessageBuilder()
        message = Message.from_dict(builder.message.dict(), bot)
        assert message.entities.mentions == []


class TestReply:
    def test_reply_in_message(self, message) -> None:
        builder = MessageBuilder()
        builder.reply(message=message)
        assert builder.message.entities.reply.source_sync_id == message.sync_id

    def test_reply_not_in_message(self) -> None:
        builder = MessageBuilder()
        with pytest.raises(AttributeError):
            builder.message.entities.reply


class TestForward:
    def test_forward_in_message(self, message) -> None:
        builder = MessageBuilder()
        builder.forward(message=message)
        assert builder.message.entities.forward.source_sync_id == message.sync_id

    def test_forward_not_in_message(self) -> None:
        builder = MessageBuilder()
        with pytest.raises(AttributeError):
            builder.message.entities.forward
