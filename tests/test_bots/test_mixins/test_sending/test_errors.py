import pytest

from botx import ServerUnknownError

pytestmark = pytest.mark.asyncio


async def test_error_for_sending_to_unknown_host(bot, message):
    bot.known_hosts = []
    with pytest.raises(ServerUnknownError):
        await bot.answer_message("some text", message)
