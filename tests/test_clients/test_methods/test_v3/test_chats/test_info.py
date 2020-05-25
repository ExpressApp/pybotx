import uuid

import pytest

from botx.clients.methods.v3.chats.info import Info

pytestmark = pytest.mark.asyncio


async def test_retrieving_info(client):
    method = Info(group_chat_id=uuid.uuid4())

    info = await method.call(client.bot.client, "example.cts")
    assert info.members

    assert client.requests[0].group_chat_id == method.group_chat_id