import uuid

import httpx
import pytest

from botx.clients.methods.errors.chat_not_found import (
    ChatNotFoundData,
    ChatNotFoundError,
)
from botx.clients.methods.v3.chats.add_user import AddUser
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_chat_not_found(client, requests_client):
    method = AddUser(group_chat_id=uuid.uuid4(), user_huids=[uuid.uuid4()])

    errors_to_raise = {
        AddUser: (
            httpx.codes.NOT_FOUND,
            ChatNotFoundData(group_chat_id=method.group_chat_id),
        ),
    }

    with client.error_client(errors=errors_to_raise):
        with pytest.raises(ChatNotFoundError):
            await callable_to_coroutine(requests_client.call, method, "example.cts")
