import pytest

from botx import ExpressServer, ServerUnknownError

pytestmark = pytest.mark.asyncio


def test_raising_error_if_token_was_not_found(client, incoming_message):
    server = client.bot.get_cts_by_host(incoming_message.user.host)
    server.server_credentials = None
    with pytest.raises(ValueError):
        client.bot.get_token_for_cts(incoming_message.user.host)


def test_raising_error_if_cts_not_found(bot, incoming_message):
    bot.known_hosts = [
        ExpressServer(host="cts.unknown1.com", secret_key="secret"),
        ExpressServer(host="cts.unknown2.com", secret_key="secret"),
    ]
    with pytest.raises(ServerUnknownError):
        bot.get_cts_by_host(incoming_message.user.host)
