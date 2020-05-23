import uuid

import pytest

from botx.clients.methods.v3.chats.stealth_set import StealthSet

pytestmark = pytest.mark.asyncio


async def test_enabling_stealth(client):
    method = StealthSet(group_chat_id=uuid.uuid4())
    method.fill_credentials("example.cts", "")

    assert await method.call(client.bot.client)

    assert client.requests[0].group_chat_id == method.group_chat_id
