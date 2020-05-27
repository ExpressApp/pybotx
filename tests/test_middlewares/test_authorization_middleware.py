import pytest

from botx.middlewares.authorization import AuthorizationMiddleware

pytestmark = pytest.mark.asyncio


async def test_obtaining_token_if_not_set(client, incoming_message):
    bot = client.bot
    bot.add_middleware(AuthorizationMiddleware)
    server = bot.get_cts_by_host(incoming_message.user.host)
    server.server_credentials = None

    await client.send_command(incoming_message)

    assert bot.get_token_for_cts(incoming_message.user.host)


async def test_doing_nothing_if_token_present(client, incoming_message):
    bot = client.bot
    bot.add_middleware(AuthorizationMiddleware)
    token = bot.get_token_for_cts(incoming_message.user.host)

    await client.send_command(incoming_message)

    assert bot.get_token_for_cts(incoming_message.user.host) == token
