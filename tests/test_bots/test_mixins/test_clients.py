import uuid

import pytest

from botx import BotXCredentials
from botx.exceptions import TokenError, UnknownBotError

pytestmark = pytest.mark.asyncio


def test_raising_error_if_token_was_not_found(client, incoming_message):
    account = client.bot.get_account_by_bot_id(incoming_message.bot_id)
    account.token = None
    with pytest.raises(TokenError):
        client.bot.get_token_for_bot(incoming_message.bot_id)


def test_get_token_to_bot(client, incoming_message):
    account = client.bot.get_account_by_bot_id(incoming_message.bot_id)
    account.token = "token"
    assert client.bot.get_token_for_bot(incoming_message.bot_id) is not None


def test_raising_error_if_cts_not_found(bot, incoming_message):
    bot.bot_accounts = [
        BotXCredentials(
            host="cts.unknown1.com",
            secret_key="secret",
            bot_id=uuid.uuid4(),
        ),
        BotXCredentials(
            host="cts.unknown2.com",
            secret_key="secret",
            bot_id=uuid.uuid4(),
        ),
    ]
    with pytest.raises(UnknownBotError):
        bot.get_account_by_bot_id(incoming_message.bot_id)
