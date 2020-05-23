import uuid

import pytest

from botx.clients.methods.v3.chats.remove_user import RemoveUser

pytestmark = pytest.mark.asyncio


async def test_removing_users(client):
    method = RemoveUser(
        group_chat_id=uuid.uuid4(), user_huids=[uuid.uuid4() for _ in range(10)]
    )
    method.fill_credentials("example.cts", "")

    assert await method.call(client.bot.client)

    assert client.requests[0].group_chat_id == method.group_chat_id
