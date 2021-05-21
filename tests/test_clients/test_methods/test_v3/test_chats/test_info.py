import uuid

import pytest

from botx.clients.methods.v3.chats.info import Info
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio


async def test_retrieving_info(client, requests_client):
    method = Info(host="example.com", group_chat_id=uuid.uuid4())

    request = requests_client.build_request(method)
    response = await callable_to_coroutine(requests_client.execute, request)
    info = await callable_to_coroutine(
        requests_client.process_response,
        method,
        response,
    )

    assert info.members

    assert client.requests[0].group_chat_id == method.group_chat_id
