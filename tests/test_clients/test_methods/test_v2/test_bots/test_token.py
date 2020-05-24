import uuid

import pytest

from botx.clients.methods.v2.bots.token import Token

pytestmark = pytest.mark.asyncio


async def test_obtaining_token(client):
    method = Token(bot_id=uuid.uuid4(), signature="signature")

    await method.call(client.bot.client, "example.cts")

    assert client.requests[0].bot_id == method.bot_id
    assert client.requests[0].signature == method.signature
