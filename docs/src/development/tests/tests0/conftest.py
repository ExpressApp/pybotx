from uuid import UUID

import pytest

from botx import Bot, BotXCredentials, MessageBuilder, TestClient

from .bot import bot


@pytest.fixture
def builder() -> MessageBuilder:
    builder = MessageBuilder()
    builder.user.host = "example.com"
    return builder


@pytest.fixture
def bot(builder: MessageBuilder) -> Bot:
    bot.bot_accounts.append(BotXCredentials(host=builder.user.host, secret_key="secret", bot_id=UUID("bot_id")))
    return bot


@pytest.fixture
def client(bot: Bot) -> TestClient:
    with TestClient(bot) as client:
        yield client
