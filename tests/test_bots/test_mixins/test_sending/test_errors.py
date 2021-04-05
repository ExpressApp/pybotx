import pytest

from botx.exceptions import UnknownBotError

pytestmark = pytest.mark.asyncio


async def test_error_for_sending_to_unknown_host(bot, message):
    bot.bot_accounts = []
    with pytest.raises(UnknownBotError):
        await bot.answer_message("some text", message)
