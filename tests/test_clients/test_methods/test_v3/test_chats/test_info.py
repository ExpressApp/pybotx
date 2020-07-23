import uuid

import pytest

from botx.clients.methods.v3.chats.info import Info
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio


async def test_retrieving_info(client, requests_client):
    method = Info(group_chat_id=uuid.uuid4())

    info = await callable_to_coroutine(requests_client.call, method, "example.cts")
    assert info.members

    assert client.requests[0].group_chat_id == method.group_chat_id
