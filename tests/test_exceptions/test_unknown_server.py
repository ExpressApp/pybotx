import pytest

from botx import ServerUnknownError

pytestmark = pytest.mark.asyncio


async def test_host_in_server_error(bot, incoming_message, client):
    bot.known_hosts = []

    with pytest.raises(ServerUnknownError) as err_info:
        await client.send_command(incoming_message)

    error = err_info.value
    assert error.host == incoming_message.user.host
