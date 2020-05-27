import pytest

from botx import ExpressServer, ServerUnknownError

pytestmark = pytest.mark.asyncio


async def test_error_when_execution_for_unknown_host(bot, client, incoming_message):
    bot.known_hosts = [
        ExpressServer(host="cts.unknown1.com", secret_key="secret"),
        ExpressServer(host="cts.unknown2.com", secret_key="secret"),
    ]
    with pytest.raises(ServerUnknownError):
        await client.send_command(incoming_message)
