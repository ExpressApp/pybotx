import uuid
from io import StringIO

from botx import (
    Entity,
    EntityTypes,
    File,
    Mention,
    MentionTypes,
    MessageBuilder,
    UserMention,
)


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

    assert builder.message.entities[0].data.mention_type == MentionTypes.user
    assert builder.message.entities[0].data.mention_data.user_huid == user_huid


def test_mention_contact_in_message():
    user_huid = uuid.uuid4()
    builder = MessageBuilder()
    builder.mention_contact(user_huid)

    assert builder.message.entities[0].data.mention_type == MentionTypes.contact
    assert builder.message.entities[0].data.mention_data.user_huid == user_huid


def test_mention_chat_in_message():
    chat_id = uuid.uuid4()
    builder = MessageBuilder()
    builder.mention_chat(chat_id)

    assert builder.message.entities[0].data.mention_type == MentionTypes.chat
    assert builder.message.entities[0].data.mention_data.group_chat_id == chat_id


def test_setting_raw_entities():
    builder = MessageBuilder()
    builder.entities = [
        Entity(
            type=EntityTypes.mention,
            data=Mention(mention_data=UserMention(user_huid=uuid.uuid4())),
        )
    ]

    assert builder.message.entities[0].data.mention_type == MentionTypes.user
