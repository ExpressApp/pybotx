import uuid
from datetime import datetime
from io import StringIO

import pytest
from pydantic import ValidationError

from botx import (
    ChatTypes,
    Entity,
    EntityTypes,
    File,
    Forward,
    Mention,
    MentionTypes,
    MessageBuilder,
    UserMention,
)
from botx.models.entities import Reply


def test_setting_new_file_from_file():
    file = File.from_string("some data", "name.txt")
    builder = MessageBuilder()
    builder.file = file

    assert builder.file == file


def test_setting_new_file_from_io():
    file = File.from_string("some data", "name.txt")
    builder = MessageBuilder()
    builder.file = file.file

    assert builder.file == file


def test_settings_new_user_for_message(incoming_message):
    builder = MessageBuilder()
    builder.user = incoming_message.user

    assert builder.user == incoming_message.user


def test_file_transfer_event():
    builder = MessageBuilder()
    builder.file = File.from_string("some data", "name.txt")

    builder.body = "file_transfer"
    builder.system_command = True


def test_setting_not_processable_file_for_incoming_message():
    file = StringIO("import this")
    file.name = "zen.py"

    builder = MessageBuilder()
    builder.file = file

    message = builder.message

    assert message.file.file_name == "zen.py"


def test_mention_user_in_message():
    user_huid = uuid.uuid4()
    builder = MessageBuilder()
    builder.mention_user(user_huid)

    assert builder.message.entities.__root__[0].data.mention_type == MentionTypes.user
    assert builder.message.entities.__root__[0].data.mention_data.user_huid == user_huid


def test_mention_contact_in_message():
    user_huid = uuid.uuid4()
    builder = MessageBuilder()
    builder.mention_contact(user_huid)

    assert (
        builder.message.entities.__root__[0].data.mention_type == MentionTypes.contact
    )
    assert builder.message.entities.__root__[0].data.mention_data.user_huid == user_huid


def test_mention_chat_in_message():
    chat_id = uuid.uuid4()
    builder = MessageBuilder()
    builder.mention_chat(chat_id)

    assert builder.message.entities.__root__[0].data.mention_type == MentionTypes.chat
    assert (
        builder.message.entities.__root__[0].data.mention_data.group_chat_id == chat_id
    )


def test_setting_raw_entities():
    builder = MessageBuilder()
    builder.entities = [
        Entity(
            type=EntityTypes.mention,
            data=Mention(mention_data=UserMention(user_huid=uuid.uuid4())),
        ),
    ]

    assert builder.message.entities.__root__[0].data.mention_type == MentionTypes.user


@pytest.mark.parametrize(
    "include_param",
    ["user_huid", "ad_login", "ad_domain", "username"],
)
def test_error_when_chat_validation_not_passed(include_param):
    user_params = {"user_huid", "ad_login", "ad_domain", "username"}
    builder = MessageBuilder()

    builder.body = "system:chat_created"
    builder.user = builder.user.copy(
        update={param: None for param in user_params - {include_param}},
    )
    builder.command_data = {
        "group_chat_id": uuid.uuid4(),
        "chat_type": "group_chat",
        "name": "",
        "creator": uuid.uuid4(),
        "members": [],
    }
    with pytest.raises(ValidationError):
        builder.system_command = True


def test_error_when_file_validation_not_passed():
    builder = MessageBuilder()
    builder.body = "file_transfer"
    with pytest.raises(ValidationError):
        builder.system_command = True


class TestBuildForward:
    def test_building_forward_via_models(self):
        builder = MessageBuilder()
        builder.forward(
            forward=Forward(
                group_chat_id=uuid.uuid4(),
                sender_huid=uuid.uuid4(),
                forward_type=ChatTypes.group_chat,  # ignore: type
                source_inserted_at=datetime.now(),
                source_sync_id=uuid.uuid4(),
            ),
        )

    def test_building_forward_via_message(self, message):
        builder = MessageBuilder()
        builder.forward(message=message)

    def test_building_forward_arguments_error(self, message):
        builder = MessageBuilder()
        with pytest.raises(ValueError):
            builder.forward(
                message=message,
                forward=Forward(
                    group_chat_id=uuid.uuid4(),
                    sender_huid=uuid.uuid4(),
                    forward_type=ChatTypes.botx,  # ignore: type
                    source_inserted_at=datetime.now(),
                    source_sync_id=uuid.uuid4(),
                ),
            )


class TestBuildReply:
    def test_building_forward_via_models(self):
        builder = MessageBuilder()
        builder.reply(
            reply=Reply(
                body="foo",
                reply_type=ChatTypes.group_chat,
                sender=uuid.uuid4(),
                source_chat_name="bar",
                source_sync_id=uuid.uuid4(),
            ),
        )

    def test_building_forward_via_message(self, message):
        builder = MessageBuilder()
        builder.reply(message=message)

    def test_building_forward_arguments_error(self, message):
        builder = MessageBuilder()
        with pytest.raises(ValueError):
            builder.reply(
                message=message,
                reply=Reply(
                    body="foo",
                    reply_type=ChatTypes.group_chat,
                    sender=uuid.uuid4(),
                    source_chat_name="bar",
                    source_sync_id=uuid.uuid4(),
                ),
            )
