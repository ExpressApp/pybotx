import pytest

from botx import Message, MessagePayload

pytestmark = pytest.mark.asyncio


async def test_filling_with_chat_id_from_credentials(client, incoming_message):
    message = Message.from_dict(incoming_message.dict(), client.bot)
    await client.bot.send_notification(
        credentials=message.credentials, payload=MessagePayload(text="some text")
    )

    assert client.notifications[0].result.body == "some text"


async def test_filling_with_ids_if_passed(client, incoming_message):
    message = Message.from_dict(incoming_message.dict(), client.bot)
    await client.bot.send_notification(
        message.credentials,
        group_chat_ids=[incoming_message.user.group_chat_id],
        payload=MessagePayload(text="some text"),
    )

    assert client.notifications[0].result.body == "some text"
