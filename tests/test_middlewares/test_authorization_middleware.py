import pytest

from botx.middlewares.authorization import AuthorizationMiddleware

pytestmark = pytest.mark.asyncio


async def test_obtaining_token_if_not_set(client, incoming_message):
    bot = client.bot
    bot.add_middleware(AuthorizationMiddleware)
    bot_account = bot.get_account_by_bot_id(incoming_message.bot_id)
    bot_account.token = None

    await client.send_command(incoming_message)

    assert bot.get_token_for_bot(incoming_message.bot_id)


async def test_doing_nothing_if_token_present(client, incoming_message):
    bot = client.bot
    bot.add_middleware(AuthorizationMiddleware)
    token = bot.get_token_for_bot(incoming_message.bot_id)

    await client.send_command(incoming_message)

    assert bot.get_token_for_bot(incoming_message.bot_id) == token
