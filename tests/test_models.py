import uuid

from pydantic import Schema

from botx import (
    CTS,
    BubbleElement,
    File,
    KeyboardElement,
    MentionTypeEnum,
    Message,
    MessageCommand,
    NotificationOpts,
    ReplyMessage,
    ResponseRecipientsEnum,
    SyncID,
)
from botx.models.base import BotXType
from botx.models.ui import UIElement


def test_botx_type_serialized_by_alias_by_default():
    class CustomType(BotXType):
        custom_field: str = Schema(..., alias="customField")

    custom_instance = CustomType(**{"customField": "some string"})
    assert custom_instance.custom_field == "some string"
    assert "customField" in custom_instance.dict()
    assert "customField" in custom_instance.json()


def test_sync_id_inits_from_uuid_and_from_uuid_init_parameters():
    custom_uuid = uuid.uuid4()

    assert SyncID(custom_uuid)
    assert SyncID(str(custom_uuid))


def test_ui_elements_get_label_anyway():
    command_text = "/handler"
    label_text = "label"

    element_with_auto_label = UIElement(command=command_text)
    assert element_with_auto_label.label == command_text

    element_with_explicit_label = UIElement(command=command_text, label=label_text)
    assert element_with_explicit_label.label == label_text


def test_cts_calculates_right_signature(host):
    bot_id = uuid.UUID("8dada2c8-67a6-4434-9dec-570d244e78ee")
    secret = "secret"
    signature = "904E39D3BC549C71F4A4BDA66AFCDA6FC90D471A64889B45CC8D2288E56526AD"

    cts = CTS(host=host, secret_key=secret)
    assert cts.calculate_signature(bot_id) == signature


def test_message_user_email(message_data):
    message = Message(**message_data())
    user = message.user
    assert user.email == f"{user.ad_login}@{user.ad_domain}"

    user.ad_login = ""
    assert not user.email


class TestMessageCommand:
    def test_command_split_body_right_with_no_whitespace(self):
        body = "/handler"
        message_command = MessageCommand(body=body, command_type="user")

        assert message_command.command == body

    def test_command_split_body_right_with_whitespaces(self):
        body = "/handler    "
        message_command = MessageCommand(body=body, command_type="user")

        assert message_command.command == body.strip()

    def test_arguments_are_empty_list_if_args_string_is_empty(self):
        body = "/handler"
        message_command = MessageCommand(body=body, command_type="user")

        assert message_command.arguments == []

    def test_arguments_are_empty_list_if_args_string_is_whitespace(self):
        body = "/handler  \t \n \v "
        message_command = MessageCommand(body=body, command_type="user")

        assert message_command.arguments == []

    def test_arguments_are_list_of_strings_if_args_string_is_words_string(self):
        arguments = ["arg1", "arg2", "arg3", "arg4"]
        body = f"/handler {' '.join(arguments)}"
        message_command = MessageCommand(body=body, command_type="user")

        assert message_command.arguments == arguments

    def test_single_argument_property(self):
        arguments = ["arg1", "arg2", "arg3", "arg4"]
        body = f"/handler {' '.join(arguments)}"
        message_command = MessageCommand(body=body, command_type="user")

        assert message_command.single_argument == " ".join(arguments)


class TestMessage:
    def test_sync_id_in_message_is_sync_id_instance(self, message_data):
        message = Message(**message_data())

        assert isinstance(message.sync_id, SyncID)

    def test_message_attributes(self, message_data):
        message = Message(**message_data())

        assert message.body == message.command.body
        assert message.data == message.command.data
        assert message.user_huid == message.user.user_huid
        assert message.ad_login == message.user.ad_login
        assert message.group_chat_id == message.user.group_chat_id
        assert message.chat_type == message.user.chat_type
        assert message.host == message.user.host


class TestFile:
    def test_file_converts_from_text_io(self, json_file_content):
        with open("tests/files/file.json") as f:
            file = File.from_file(f)

        assert file.raw_data.decode() == json_file_content

    def test_file_converts_from_bytes_io(self, gif_file_content):
        with open("tests/files/file.gif", "rb") as f:
            file = File.from_file(f)

        assert file.raw_data == gif_file_content

    def test_file_property_file_is_file_like_object(self, json_file_content):
        with open("tests/files/file.json") as f:
            file = File.from_file(f)

        with file.file as f:
            assert f.read().decode() == json_file_content

    def test_file_media_type_splited_right_from_data_string(self):
        with open("tests/files/file.txt") as f:
            file = File.from_file(f)
            assert file.media_type == "text/plain"

        with open("tests/files/file.json") as f:
            file = File.from_file(f)
            assert file.media_type == "application/json"

        with open("tests/files/file.gif", "rb") as f:
            file = File.from_file(f)
            assert file.media_type == "image/gif"

        with open("tests/files/file.png", "rb") as f:
            file = File.from_file(f)
            assert file.media_type == "image/png"


class TestReplyMessage:
    def test_creating_from_message(self, message_data):
        message = Message(**message_data())

        reply = ReplyMessage.from_message("text", message)

        assert reply.text == "text"
        assert reply.chat_id == message.sync_id
        assert isinstance(reply.chat_id, SyncID)
        assert reply.bot_id == message.bot_id
        assert reply.host == message.host

    def test_group_chat_ids_assigning(self, reply_message):
        chat_ids = [uuid.uuid4() for _ in range(4)]
        reply_message.chat_id = chat_ids[0]
        assert reply_message.chat_id == chat_ids[0]

        reply_message.chat_id = chat_ids
        assert reply_message.chat_id == chat_ids

    def test_file_property(self, reply_message, tmpdir):
        with open(tmpdir / "tmp.txt", "w") as f:
            f.write("some text")

        with open(tmpdir / "tmp.txt") as f:
            reply_message.add_file(f)

        with open(tmpdir / "tmp.txt") as f:
            assert reply_message.file == File.from_file(f)

    def test_user_mentioning(self, reply_message):
        user_huid = uuid.uuid4()
        reply_message.mention_user(user_huid)
        assert reply_message.mentions

        mention = reply_message.mentions[0]

        assert mention.mention_type == MentionTypeEnum.user
        assert mention.mention_data.user_huid == user_huid

    def test_recipients_adding(self, reply_message):
        users = [uuid.uuid4() for _ in range(4)]
        reply_message.add_recipient(users[0])
        reply_message.add_recipient(users[1])
        assert reply_message.recipients == users[0:2]

        reply_message.recipients = ResponseRecipientsEnum.all
        reply_message.add_recipients([users[0]])
        reply_message.add_recipients(users[1:])
        assert reply_message.recipients == users

    def test_notification_options(self, reply_message):
        assert reply_message.opts == NotificationOpts()

        reply_message.show_notification(False)
        assert not reply_message.opts.send

        reply_message.force_notification(True)
        assert reply_message.opts.force_dnd

    def test_bubble_adding(self, reply_message):
        cmd_text = "/cmd"

        reply_message.add_bubble(cmd_text)

        bubble_element = reply_message.bubble[0][0]
        assert bubble_element == BubbleElement(command=cmd_text)

    def test_adding_rows_to_bubble(self, reply_message):
        reply_message.add_bubble("/cmd")

        reply_message.add_bubble("/cmd2", new_row=False)
        assert len(reply_message.bubble[0]) == 2

        reply_message.add_bubble("/cmd3")
        assert len(reply_message.bubble) == 2

    def test_keyboard_adding(self, reply_message):
        cmd_text = "/cmd"

        reply_message.add_keyboard_button(cmd_text)

        keyboard_element = reply_message.keyboard[0][0]
        assert keyboard_element == KeyboardElement(command=cmd_text)

    def test_adding_rows_to_keyboard(self, reply_message):
        reply_message.add_keyboard_button("/cmd")

        reply_message.add_keyboard_button("/cmd2", new_row=False)
        assert len(reply_message.keyboard[0]) == 2

        reply_message.add_keyboard_button("/cmd3")
        assert len(reply_message.keyboard) == 2
