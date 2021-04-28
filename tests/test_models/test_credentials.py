from uuid import UUID

import pytest

from botx import BotXCredentials
from botx.clients.methods.v2.bots.token import Token


def test_calculating_signature_for_token(host) -> None:
    bot_id = UUID("8dada2c8-67a6-4434-9dec-570d244e78ee")
    account = BotXCredentials(
        host=host,
        secret_key="secret",
        bot_id=bot_id,
    )
    signature = "904E39D3BC549C71F4A4BDA66AFCDA6FC90D471A64889B45CC8D2288E56526AD"
    assert account.signature == signature


@pytest.mark.asyncio()
async def test_auth_to_each_known_account(bot, client) -> None:
    accounts_len = len(bot.bot_accounts)
    for account in bot.bot_accounts:
        account.token = None

    await bot.authorize()
    assert len(client.requests) == accounts_len

    for request in client.requests:
        assert isinstance(request, Token)

    for account in bot.bot_accounts:
        assert account.token is not None
