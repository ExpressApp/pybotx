import pytest

pytestmark = pytest.mark.asyncio


async def test_raising_error_if_token_was_not_found(client, incoming_message):
    server = client.bot.get_cts_by_host(incoming_message.user.host)
    server.server_credentials = None
    with pytest.raises(ValueError):
        client.bot.get_token_for_cts(incoming_message.user.host)
