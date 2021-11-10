import uuid

import pytest

from botx.clients.methods.v3.chats.unpin_message import UnpinMessage
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_unpinning_message(client, requests_client):
    chat_id = uuid.uuid4()
    method = UnpinMessage(host="example.com", chat_id=chat_id)

    request = requests_client.build_request(method)
    assert await callable_to_coroutine(requests_client.execute, request)

    assert client.requests[0].chat_id == method.chat_id
