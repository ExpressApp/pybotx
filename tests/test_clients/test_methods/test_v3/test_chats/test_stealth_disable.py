import uuid

import pytest

from botx.clients.methods.v3.chats.stealth_disable import StealthDisable
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_disabling_stealth(client, requests_client):
    method = StealthDisable(group_chat_id=uuid.uuid4())

    assert await callable_to_coroutine(requests_client.call, method, "example.cts")

    assert client.requests[0].group_chat_id == method.group_chat_id
