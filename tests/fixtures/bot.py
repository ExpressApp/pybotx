import pytest

from botx import Bot, BotXCredentials, TestClient


@pytest.fixture()
def bot(host, secret_key, bot_id, token):
    accounts = BotXCredentials(
        host=host,
        secret_key=secret_key,
        bot_id=bot_id,
        token=token,
    )

    return Bot(bot_accounts=[accounts])


@pytest.fixture()
def client(bot):
    with TestClient(bot) as client:
        yield client
