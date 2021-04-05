import pytest

from botx import UnknownBotError

pytestmark = pytest.mark.asyncio


async def test_host_in_server_error(bot, incoming_message, client):
    bot.bot_accounts = []

    with pytest.raises(UnknownBotError) as err_info:
        await client.send_command(incoming_message)

    error = err_info.value
    assert error.bot_id == incoming_message.bot_id
