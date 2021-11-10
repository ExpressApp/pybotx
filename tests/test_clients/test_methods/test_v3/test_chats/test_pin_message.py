import uuid

import pytest

from botx.clients.methods.v3.chats.pin_message import PinMessage
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_pinning_message(client, requests_client):
    chat_id = uuid.uuid4()
    sync_id = uuid.uuid4()
    method = PinMessage(host="example.com", chat_id=chat_id, sync_id=sync_id)

    request = requests_client.build_request(method)
    assert await callable_to_coroutine(requests_client.execute, request)

    assert client.requests[0].chat_id == method.chat_id
    assert client.requests[0].sync_id == method.sync_id
