import pytest

from botx import ChatTypes, Message

pytestmark = pytest.mark.asyncio


async def test_creating_chat(client, incoming_message):
    message = Message.from_dict(incoming_message.dict(), client.bot)
    await client.bot.create_chat(
        message.credentials,
        name="test",
        members=[message.user_huid],
        chat_type=ChatTypes.group_chat,
    )

    assert client.requests[0].name == "test"
