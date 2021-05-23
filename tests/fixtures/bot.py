import pytest

from botx import Bot, ExpressServer, ServerCredentials, TestClient


@pytest.fixture()
def bot(host, secret_key, bot_id, token):
    credentials = ServerCredentials(bot_id=bot_id, token=token)
    server = ExpressServer(
        host=host,
        secret_key=secret_key,
        server_credentials=credentials,
    )

    return Bot(known_hosts=[server])


@pytest.fixture()
def client(bot):
    with TestClient(bot) as client:
        yield client
