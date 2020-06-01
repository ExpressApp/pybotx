import pytest

from botx import File

pytestmark = pytest.mark.asyncio


@pytest.fixture()
def sending_file():
    return File.from_string("some content", "file.txt")


async def test_using_command_result(bot, client, message, sending_file):
    await bot.send_file(sending_file, message.credentials)

    message = client.command_results[0]
    assert message.file == sending_file


async def test_using_notification(bot, client, message, sending_file):
    await bot.send_file(
        sending_file, message.credentials.copy(update={"sync_id": None}),
    )

    message = client.notifications[0]
    assert message.file == sending_file
