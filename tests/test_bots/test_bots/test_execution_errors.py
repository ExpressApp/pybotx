import uuid

import pytest

from botx import BotXCredentials, UnknownBotError

pytestmark = pytest.mark.asyncio


async def test_error_when_execution_for_unknown_host(bot, client, incoming_message, bot_id):
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
        await client.send_command(incoming_message)
