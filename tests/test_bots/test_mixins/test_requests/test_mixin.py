import pytest

from botx.clients.methods.v2.bots.token import Token

pytestmark = pytest.mark.asyncio


async def test_obtain_token_if_missed(bot, client, message):
    bot.bot_accounts[0].token = None

    await bot.answer_message("some text", message)

    assert len(client.requests) == 2
    assert isinstance(client.requests[0], Token)
