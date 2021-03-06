import uuid

import pytest

from botx import File, SendingMessage

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def sending_file():
    return File.from_string("some content", "file.txt")


@pytest.fixture()
def metadata():
    return {"account_id": 94}


@pytest.fixture()
def sending_message(message, metadata, sending_file):
    sending_message = SendingMessage.from_message(
        text="some text", file=sending_file, message=message,
    )
    sending_message.add_keyboard_button(command="/command", label="keyboard")
    sending_message.add_bubble(command="/command", label="bubble")
    sending_message.metadata = metadata
    return sending_message


async def test_using_notification_route(bot, client, sending_message):
    await bot.send(sending_message)

    assert client.notifications[0]


async def test_sending_notification_using_send(bot, client, sending_message, metadata):
    sending_message.credentials.sync_id = None

    await bot.send(sending_message)

    assert len(client.notifications)
    notification = client.notifications[0]

    assert notification.result.metadata == metadata


async def test_sending_update_using_send(bot, client, sending_message):
    sending_message.credentials.message_id = uuid.uuid4()

    await bot.send(sending_message, update=True)

    assert client.message_updates[0].sync_id == sending_message.credentials.message_id


async def test_returning_event_id_from_notification(bot, client, sending_message):
    sending_message.credentials.sync_id = None
    assert await bot.send(sending_message)


async def test_setting_custom_id_for_notification(bot, client, sending_message):
    message_id = uuid.uuid4()
    sending_message.credentials.message_id = message_id
    notification_id = await bot.send(sending_message)
    assert notification_id == message_id
