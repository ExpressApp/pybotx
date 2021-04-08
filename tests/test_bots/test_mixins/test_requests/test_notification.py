import pytest

from botx import MessagePayload

pytestmark = pytest.mark.asyncio


async def test_filling_with_chat_id_from_credentials(client, message):
    await client.bot.send_notification(
        credentials=message.credentials,
        payload=MessagePayload(text="some text"),
    )

    assert client.notifications[0].result.body == "some text"


async def test_filling_with_ids_if_passed(client, message):
    await client.bot.send_notification(
        message.credentials,
        group_chat_ids=[message.user.group_chat_id],
        payload=MessagePayload(text="some text"),
    )

    assert client.notifications[0].result.body == "some text"


async def test_send_to_all_if_ids_omitted(client, message):
    text = "some text"
    credentials = message.credentials.copy(update={"chat_id": None})

    await client.bot.send_notification(credentials, MessagePayload(text=text))

    assert client.notifications[0].result.body == text


async def test_direct_notification_chat_id_required(client, message):
    credentials = message.credentials.copy(update={"chat_id": None})

    with pytest.raises(ValueError) as exc:
        await client.bot.send_direct_notification(
            credentials,
            payload=MessagePayload(text="some text"),
        )

    assert "chat_id is required" in str(exc.value)
