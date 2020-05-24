import uuid

import pytest
from httpx import StatusCode

from botx.clients.methods.errors.chat_not_found import (
    ChatNotFoundData,
    ChatNotFoundError,
)
from botx.clients.methods.v3.chats.add_user import AddUser

pytestmark = pytest.mark.asyncio


async def test_raising_chat_not_found(client):
    method = AddUser(group_chat_id=uuid.uuid4(), user_huids=[uuid.uuid4()])

    errors_to_raise = {
        AddUser: (
            StatusCode.NOT_FOUND,
            ChatNotFoundData(group_chat_id=method.group_chat_id),
        )
    }

    with pytest.raises(ChatNotFoundError):
        with client.error_client(errors=errors_to_raise):
            await method.call(client.bot.client, "example.cts")
