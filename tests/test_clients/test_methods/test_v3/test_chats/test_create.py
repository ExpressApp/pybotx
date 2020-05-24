import uuid

import pytest

from botx import ChatTypes
from botx.clients.methods.v3.chats.create import Create

pytestmark = pytest.mark.asyncio


async def test_chat_creation(client):
    method = Create(
        name="test name", members=[uuid.uuid4()], chat_type=ChatTypes.group_chat
    )

    assert await method.call(client.bot.client, "example.cts")

    assert client.requests[0].name == method.name
    assert client.requests[0].members == method.members
