import pytest

from botx import MessagePayload

pytestmark = pytest.mark.asyncio


async def test_filling_with_chat_id_from_credentials(client, message):
    await client.bot.send_notification(
        credentials=message.credentials, payload=MessagePayload(text="some text")
    )

    assert client.notifications[0].result.body == "some text"


async def test_filling_with_ids_if_passed(client, message):
    await client.bot.send_notification(
        message.credentials,
        group_chat_ids=[message.user.group_chat_id],
        payload=MessagePayload(text="some text"),
    )

    assert client.notifications[0].result.body == "some text"
