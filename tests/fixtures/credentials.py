import uuid

import pytest


@pytest.fixture()
def host():
    return "cts.example.com"


@pytest.fixture()
def secret_key():
    return "secret-key-for-token"


@pytest.fixture()
def token():
    return "generated-token-for-bot"


@pytest.fixture()
def bot_id():
    return uuid.uuid4()
