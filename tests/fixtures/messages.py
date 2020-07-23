import pytest

from botx import ChatCreatedEvent, Message, MessageBuilder, UserKinds
from botx.models.events import UserInChatCreated


@pytest.fixture()
def incoming_message(host, bot_id):
    builder = MessageBuilder()
    builder.bot_id = bot_id
    builder.user.host = host
    return builder.message


@pytest.fixture()
def message(incoming_message, bot):
    return Message.from_dict(incoming_message.dict(), bot)


@pytest.fixture()
def chat_created_message(host, bot_id):
    builder = MessageBuilder()
    builder.bot_id = bot_id
    builder.command_data = ChatCreatedEvent(
        group_chat_id=builder.user.group_chat_id,
        chat_type=builder.user.chat_type,
        name="chat",
        creator=builder.user.user_huid,
        members=[
            UserInChatCreated(
                huid=builder.user.user_huid,
                user_kind=UserKinds.user,
                name=builder.user.username,
                admin=True,
            ),
            UserInChatCreated(
                huid=builder.bot_id, user_kind=UserKinds.bot, name="bot", admin=False,
            ),
        ],
    )
    builder.user.user_huid = None
    builder.user.ad_login = None
    builder.user.ad_domain = None
    builder.user.username = None

    builder.body = "system:chat_created"
    builder.system_command = True

    return builder.message
