import uuid

import pytest

from botx.clients.methods.v3.chats.stealth_disable import StealthDisable

pytestmark = pytest.mark.asyncio


async def test_disabling_stealth(client):
    method = StealthDisable(group_chat_id=uuid.uuid4())

    assert await method.call(client.bot.client, "example.cts")

    assert client.requests[0].group_chat_id == method.group_chat_id
