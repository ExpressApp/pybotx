import pytest

from botx import File

pytestmark = pytest.mark.asyncio


async def test_answer_message_is_notification(bot, client, message):
    await bot.answer_message("some text", message)

    message = client.notifications[0]
    assert message.result.body == "some text"


async def test_answer_message_with_file_is_notification(bot, client, message):
    file = File.from_string("some content", "file.txt")
    await bot.answer_message(
        "some text",
        message,
        file=file,
    )

    message = client.notifications[0]
    assert message.result.body == "some text"
    assert message.file == file


async def test_answer_message_with_metadata(bot, client, message):
    await bot.answer_message("some text", message, metadata={"foo": "bar"})

    message = client.notifications[0]
    assert message.result.metadata == {"foo": "bar"}
