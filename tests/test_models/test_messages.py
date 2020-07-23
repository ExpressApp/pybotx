import uuid
from io import BytesIO, StringIO

import pytest

from botx import (
    Bot,
    BubbleElement,
    ChatMention,
    File,
    IncomingMessage,
    KeyboardElement,
    Mention,
    MentionTypes,
    Message,
    MessageMarkup,
    MessageOptions,
    NotificationOptions,
    Recipients,
    SendingCredentials,
    SendingMessage,
    UserMention,
)
from botx.testing import MessageBuilder


@pytest.fixture
def incoming_message() -> IncomingMessage:
    return IncomingMessage.parse_obj(
        {
            "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
            "command": {
                "body": "system:chat_created",
                "command_type": "system",
                "data": {
                    "group_chat_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                    "chat_type": "group_chat",
                    "name": "Meeting Room",
                    "creator": "ab103983-6001-44e9-889e-d55feb295494",
                    "members": [
                        {
                            "huid": "ab103983-6001-44e9-889e-d55feb295494",
                            "name": "Bob",
                            "user_kind": "user",
                            "admin": True,
                        },
                        {
                            "huid": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
                            "name": "Funny Bot",
                            "user_kind": "botx",
                            "admin": False,
                        },
                    ],
                },
            },
            "file": None,
            "from": {
                "user_huid": None,
                "group_chat_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                "ad_login": None,
                "ad_domain": None,
                "username": None,
                "chat_type": "group_chat",
                "host": "cts.ccteam.ru",
                "is_admin": False,
                "is_creator": False,
            },
            "bot_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
            "entities": [
                {
                    "type": "mention",
                    "data": {
                        "mention_type": "contact",
                        "mention_id": "c06a96fa-7881-0bb6-0e0b-0af72fe3683f",
                        "mention_data": {
                            "user_huid": "ab103983-6001-44e9-889e-d55feb295494",
                            "name": "User",
                        },
                    },
                }
            ],
        }
    )


def test_setting_ui_flag_property_for_common_message() -> None:
    msg = Message.from_dict(
        {
            "sync_id": "a465f0f3-1354-491c-8f11-f400164295cb",
            "command": {"body": "/cmd", "command_type": "user", "data": {"ui": True}},
            "file": None,
            "from": {
                "user_huid": None,
                "group_chat_id": "8dada2c8-67a6-4434-9dec-570d244e78ee",
                "ad_login": None,
                "ad_domain": None,
                "username": None,
                "chat_type": "group_chat",
                "host": "cts.ccteam.ru",
                "is_admin": False,
                "is_creator": False,
            },
            "bot_id": "dcfa5a7c-7cc4-4c89-b6c0-80325604f9f4",
        },
        Bot(),
    )

    assert msg.sent_from_button


def test_setting_ui_flag_property_for_system_message(incoming_message) -> None:
    msg = Message.from_dict(incoming_message.dict(), Bot())
    assert not msg.sent_from_button


@pytest.fixture
def sending_message() -> SendingMessage:
    return SendingMessage(
        text="text",
        file=File.from_string(b"data", filename="file.txt"),
        credentials=SendingCredentials(
            sync_id=uuid.uuid4(), bot_id=uuid.uuid4(), host="host"
        ),
        markup=MessageMarkup(
            bubbles=[[BubbleElement(command="")]],
            keyboard=[[KeyboardElement(command="")]],
        ),
        options=MessageOptions(
            recipients=[uuid.uuid4()],
            mentions=[
                Mention(mention_data=UserMention(user_huid=uuid.uuid4())),
                Mention(
                    mention_data=UserMention(user_huid=uuid.uuid4()),
                    mention_type=MentionTypes.contact,
                ),
                Mention(
                    mention_data=ChatMention(group_chat_id=uuid.uuid4()),
                    mention_type=MentionTypes.chat,
                ),
            ],
            notifications=NotificationOptions(send=False, force_dnd=True),
        ),
    )


def test_message_is_proxy_to_incoming_message(incoming_message) -> None:
    msg = Message.from_dict(incoming_message.dict(), Bot())
    assert msg.sync_id == incoming_message.sync_id
    assert msg.command == incoming_message.command
    assert msg.file == incoming_message.file
    assert msg.user == incoming_message.user
    assert msg.bot_id == incoming_message.bot_id
    assert msg.body == incoming_message.command.body
    assert msg.data == incoming_message.command.data_dict
    assert msg.user_huid == incoming_message.user.user_huid
    assert msg.ad_login == incoming_message.user.ad_login
    assert msg.group_chat_id == incoming_message.user.group_chat_id
    assert msg.chat_type == incoming_message.user.chat_type.value
    assert msg.host == incoming_message.user.host
    assert msg.credentials.sync_id == incoming_message.sync_id
    assert msg.credentials.bot_id == incoming_message.bot_id
    assert msg.credentials.host == incoming_message.user.host
    assert msg.entities == incoming_message.entities
    assert msg.incoming_message == incoming_message


class TestBuildingSendingMessage:
    def test_building_from_message(self, sending_message: SendingMessage) -> None:
        builder = MessageBuilder()
        msg = Message(message=builder.message, bot=Bot())
        sending_msg = SendingMessage.from_message(
            text=sending_message.text, message=msg
        )
        assert sending_msg.host == msg.host
        assert sending_msg.sync_id == msg.sync_id
        assert sending_msg.bot_id == msg.bot_id

    class TestCredentialsBuilding:
        def test_only_credentials_or_separate_credential_parts(
            self, sending_message: SendingMessage
        ) -> None:
            with pytest.raises(AssertionError):
                _ = SendingMessage(
                    sync_id=sending_message.sync_id,
                    bot_id=sending_message.bot_id,
                    host=sending_message.host,
                    credentials=sending_message.credentials,
                )

        def test_credentials_will_be_built_from_credential_parts(
            self, sending_message: SendingMessage
        ) -> None:
            msg = SendingMessage(
                text=sending_message.text,
                sync_id=sending_message.sync_id,
                bot_id=sending_message.bot_id,
                host=sending_message.host,
            )
            assert msg.credentials == sending_message.credentials

        def test_merging_message_id_into_credentials(
            self, sending_message: SendingMessage
        ) -> None:
            message_id = uuid.uuid4()
            msg = SendingMessage(
                text=sending_message.text,
                credentials=sending_message.credentials,
                message_id=message_id,
            )
            assert msg.credentials.message_id == message_id

        def test_leaving_credentials_message_id_into_credentials_if_was_set(
            self, sending_message: SendingMessage
        ) -> None:
            message_id = uuid.uuid4()
            sending_message.credentials.message_id = message_id
            msg = SendingMessage(
                text=sending_message.text,
                credentials=sending_message.credentials,
                message_id=uuid.uuid4(),
            )
            assert msg.credentials.message_id == sending_message.credentials.message_id

    class TestMarkupBuilding:
        def test_markup_creation_from_bubbles(
            self, sending_message: SendingMessage
        ) -> None:
            msg = SendingMessage(
                text=sending_message.text,
                credentials=sending_message.credentials,
                bubbles=sending_message.markup.bubbles,
            )
            assert msg.markup.keyboard == []
            assert msg.markup.bubbles == sending_message.markup.bubbles

        def test_markup_creation_from_keyboard(
            self, sending_message: SendingMessage
        ) -> None:
            msg = SendingMessage(
                text=sending_message.text,
                credentials=sending_message.credentials,
                keyboard=sending_message.markup.keyboard,
            )
            assert msg.markup.keyboard == sending_message.markup.keyboard
            assert msg.markup.bubbles == []

        def test_markup_creation_from_bubbles_and_keyboard(
            self, sending_message: SendingMessage
        ) -> None:
            msg = SendingMessage(
                text=sending_message.text,
                credentials=sending_message.credentials,
                bubbles=sending_message.markup.bubbles,
                keyboard=sending_message.markup.keyboard,
            )
            assert msg.markup == sending_message.markup

        def test_only_markup_or_separate_markup_parts(
            self, sending_message: SendingMessage
        ) -> None:
            with pytest.raises(AssertionError):
                _ = SendingMessage(
                    text=sending_message.text,
                    credentials=sending_message.credentials,
                    bubbles=sending_message.markup.bubbles,
                    keyboard=sending_message.markup.keyboard,
                    markup=sending_message.markup,
                )

    class TestOptionsBuilding:
        def test_options_from_mentions(self, sending_message: SendingMessage) -> None:
            msg = SendingMessage(
                text=sending_message.text,
                credentials=sending_message.credentials,
                mentions=sending_message.options.mentions,
            )
            assert msg.options.mentions == sending_message.options.mentions

        def test_options_from_recipients(self, sending_message: SendingMessage) -> None:
            msg = SendingMessage(
                text=sending_message.text,
                credentials=sending_message.credentials,
                recipients=sending_message.options.recipients,
            )
            assert msg.options.recipients == sending_message.options.recipients

        def test_options_from_notification_options(
            self, sending_message: SendingMessage
        ) -> None:
            msg = SendingMessage(
                text=sending_message.text,
                credentials=sending_message.credentials,
                notification_options=sending_message.options.notifications,
            )
            assert msg.options.notifications == sending_message.options.notifications

        def test_option_from_message_options(
            self, sending_message: SendingMessage
        ) -> None:
            msg = SendingMessage(
                text=sending_message.text,
                credentials=sending_message.credentials,
                options=sending_message.options,
            )
            assert msg.options == sending_message.options

        def test_only_options_or_separate_options_parts(
            self, sending_message: SendingMessage
        ) -> None:
            with pytest.raises(AssertionError):
                _ = SendingMessage(
                    text=sending_message.text,
                    credentials=sending_message.credentials,
                    options=sending_message.options,
                    mentions=sending_message.options.mentions,
                    recipients=sending_message.options.recipients,
                    notification_options=sending_message.options.notifications,
                )


class TestSendingMessageProperties:
    def test_message_text(self, sending_message: SendingMessage) -> None:
        sending_message.text = "test"
        assert sending_message.text == "test"

    class TestMessageFile:
        def test_message_file(self, sending_message: SendingMessage) -> None:
            file = sending_message.file
            sending_message.file = file
            assert sending_message.file == file

        def test_message_file_from_file(self, sending_message: SendingMessage) -> None:
            original_file = sending_message.file
            sending_message.add_file(File.from_file(original_file.file))
            assert sending_message.file == original_file

        def test_message_file_from_string_file(
            self, sending_message: SendingMessage
        ) -> None:
            original_file = sending_message.file
            sending_message.add_file(
                StringIO(original_file.file.read().decode()),
                filename=original_file.file_name,
            )
            assert sending_message.file == original_file

        def test_message_file_from_bytes_file(
            self, sending_message: SendingMessage
        ) -> None:
            original_file = sending_message.file
            sending_message.add_file(
                BytesIO(original_file.file.read()), filename=original_file.file_name
            )
            assert sending_message.file == original_file

    def test_message_markup(self, sending_message: SendingMessage) -> None:
        markup = MessageMarkup(bubbles=[[BubbleElement(command="/test")]])
        sending_message.markup = markup
        assert sending_message.markup == markup

    def test_message_options(self, sending_message: SendingMessage) -> None:
        options = MessageOptions()
        sending_message.options = options
        assert sending_message.options == options

    def test_message_sync_id(self, sending_message: SendingMessage) -> None:
        sync_id = uuid.uuid4()
        sending_message.sync_id = sync_id
        assert sending_message.sync_id == sync_id

    def test_message_chat_id(self, sending_message: SendingMessage) -> None:
        chat_id = uuid.uuid4()
        sending_message.chat_id = chat_id
        assert sending_message.chat_id == chat_id

    def test_message_bot_id(self, sending_message: SendingMessage) -> None:
        bot_id = uuid.uuid4()
        sending_message.bot_id = bot_id
        assert sending_message.bot_id == bot_id

    def test_message_host(self, sending_message: SendingMessage) -> None:
        host = "example.com"
        sending_message.host = host
        assert sending_message.host == host

    class TestMentioning:
        def test_mentioning_user(self, sending_message: SendingMessage) -> None:
            sending_message.payload.options.mentions = []
            user_huid = uuid.uuid4()
            user_name = "test"
            sending_message.mention_user(user_huid, user_name)
            mention = sending_message.payload.options.mentions[0]
            assert mention.mention_type == MentionTypes.user

        def test_mentioning_contact(self, sending_message: SendingMessage) -> None:
            sending_message.payload.options.mentions = []
            user_huid = uuid.uuid4()
            user_name = "test"
            sending_message.mention_contact(user_huid, user_name)
            mention = sending_message.payload.options.mentions[0]
            assert mention.mention_type == MentionTypes.contact

        def test_mentioning_chat(self, sending_message: SendingMessage) -> None:
            sending_message.payload.options.mentions = []
            chat_id = uuid.uuid4()
            chat_name = "test"
            sending_message.mention_chat(chat_id, chat_name)
            mention = sending_message.payload.options.mentions[0]
            assert mention.mention_type == MentionTypes.chat

    class TestAddingRecipients:
        def test_adding_recipients_separately(
            self, sending_message: SendingMessage
        ) -> None:
            users = [uuid.uuid4(), uuid.uuid4()]
            sending_message.payload.options.recipients = Recipients.all

            sending_message.add_recipient(users[0])
            assert sending_message.options.recipients == [users[0]]

            sending_message.add_recipient(users[1])
            assert sending_message.options.recipients == users

        def test_adding_multiple_recipients(
            self, sending_message: SendingMessage
        ) -> None:
            users = [uuid.uuid4(), uuid.uuid4()]
            sending_message.payload.options.recipients = Recipients.all

            sending_message.add_recipients(users[:1])
            assert sending_message.options.recipients == users[:1]

            sending_message.add_recipients(users[1:])
            assert sending_message.options.recipients == users

    class TestMarkupAdding:
        def test_adding_bubbles(self, sending_message: SendingMessage) -> None:
            bubble = BubbleElement(command="/test")
            sending_message.markup = MessageMarkup()
            sending_message.add_bubble("/test")
            sending_message.add_bubble("/test", new_row=False)
            sending_message.add_bubble("/test")
            sending_message.add_bubble("/test")
            sending_message.add_bubble("/test", new_row=False)
            assert sending_message.markup == MessageMarkup(
                bubbles=[[bubble, bubble], [bubble], [bubble, bubble]]
            )

        def test_adding_keyboard(self, sending_message: SendingMessage) -> None:
            keyboard_button = KeyboardElement(command="/test")
            sending_message.markup = MessageMarkup()
            sending_message.add_keyboard_button("/test")
            sending_message.add_keyboard_button("/test", new_row=False)
            sending_message.add_keyboard_button("/test")
            sending_message.add_keyboard_button("/test")
            sending_message.add_keyboard_button("/test", new_row=False)
            assert sending_message.markup == MessageMarkup(
                keyboard=[
                    [keyboard_button, keyboard_button],
                    [keyboard_button],
                    [keyboard_button, keyboard_button],
                ]
            )

    def test_setting_notification_show(self, sending_message: SendingMessage) -> None:
        sending_message.show_notification(True)
        assert sending_message.options.notifications.send

    def test_setting_dnd(self, sending_message: SendingMessage) -> None:
        sending_message.force_notification(True)
        assert sending_message.options.notifications.force_dnd
