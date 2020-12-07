import pytest

from botx import File

pytestmark = pytest.mark.asyncio


async def test_sending_command_result(bot, client, message):
    await bot.send_message(
        "some text", message.credentials,
    )

    assert client.notifications[0]


async def test_sending_notification_using_send_message(bot, client, message):
    await bot.send_message(
        "some text", message.credentials.copy(update={"sync_id": None}),
    )

    assert client.notifications[0]


async def test_adding_file(bot, client, message):
    sending_file = File.from_string("some content", "file.txt")
    await bot.send_message(
        "some text", message.credentials, file=sending_file.file,
    )

    command_result = client.notifications[0]
    assert command_result.file == sending_file
