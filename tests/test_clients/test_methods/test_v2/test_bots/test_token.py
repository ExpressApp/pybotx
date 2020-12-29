import uuid

import pytest

from botx.clients.methods.v2.bots.token import Token
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_obtaining_token(client, requests_client):
    method = Token(bot_id=uuid.uuid4(), signature="signature")

    method.host = "example.com"
    request = requests_client.build_request(method)
    await callable_to_coroutine(requests_client.execute, method, request)

    assert client.requests[0].bot_id == method.bot_id
    assert client.requests[0].signature == method.signature
