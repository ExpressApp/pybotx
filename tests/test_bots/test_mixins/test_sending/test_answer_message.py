import pytest

from botx import File

pytestmark = pytest.mark.asyncio


async def test_send_command_result(bot, client, message):
    await bot.answer_message("some text", message)

    message = client.command_results[0]
    assert message.result.body == "some text"


async def test_sending_command_result_with_file(bot, client, message):
    file = File.from_string("some content", "file.txt")
    await bot.answer_message(
        "some text", message, file=file,
    )

    message = client.command_results[0]
    assert message.result.body == "some text"
    assert message.file == file
