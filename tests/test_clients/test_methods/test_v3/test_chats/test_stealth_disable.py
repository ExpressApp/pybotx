import uuid

import pytest

from botx.clients.methods.v3.chats.stealth_disable import StealthDisable
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_disabling_stealth(client, requests_client):
    method = StealthDisable(host="example.com", group_chat_id=uuid.uuid4())

    request = requests_client.build_request(method)
    assert await callable_to_coroutine(requests_client.execute, request)

    assert client.requests[0].group_chat_id == method.group_chat_id
