import uuid

import pytest

from botx.clients.methods.v3.chats.add_user import AddUser
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio


async def test_adding_users(client, requests_client):
    method = AddUser(
        group_chat_id=uuid.uuid4(), user_huids=[uuid.uuid4() for _ in range(10)],
    )

    assert await callable_to_coroutine(requests_client.call, method, "example.cts")

    assert client.requests[0].group_chat_id == method.group_chat_id
    assert client.requests[0].user_huids == method.user_huids
