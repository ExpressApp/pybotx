import uuid

import pytest

from botx.clients.methods.v3.chats.chat_list import ChatList
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio


async def test_retrieving_bot_chats(client, requests_client):
    method = ChatList(host="example.com")

    request = requests_client.build_request(method)
    response = await callable_to_coroutine(requests_client.execute, request)
    bot_chats = await callable_to_coroutine(
        requests_client.process_response,
        method,
        response,
    )

    assert list(bot_chats)

    assert len(bot_chats[0].members) == 1
