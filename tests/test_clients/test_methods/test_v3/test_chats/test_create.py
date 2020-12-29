import uuid

import pytest

from botx import ChatTypes
from botx.clients.methods.v3.chats.create import Create
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio


async def test_chat_creation(client, requests_client):
    method = Create(
        name="test name", members=[uuid.uuid4()], chat_type=ChatTypes.group_chat,
    )

    method.host = "example.com"
    request = requests_client.build_request(method)
    await callable_to_coroutine(requests_client.execute, method, request)

    assert client.requests[0].name == method.name
    assert client.requests[0].members == method.members
