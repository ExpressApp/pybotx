import pytest

from botx import Bot, ExpressServer, MessageBuilder, TestClient

from .bot import bot


@pytest.fixture
def builder() -> MessageBuilder:
    builder = MessageBuilder()
    builder.user.host = "example.com"
    return builder


@pytest.fixture
def bot(builder: MessageBuilder) -> Bot:
    bot.known_hosts.append(ExpressServer(host=builder.user.host, secret_key="secret"))
    return bot


@pytest.fixture
def client(bot: Bot) -> TestClient:
    with TestClient(bot) as client:
        yield client
