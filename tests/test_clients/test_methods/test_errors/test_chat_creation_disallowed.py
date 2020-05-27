import uuid

import pytest
from httpx import StatusCode

from botx import ChatTypes
from botx.clients.methods.errors.chat_creation_disallowed import (
    ChatCreationDisallowedData,
    ChatCreationDisallowedError,
)
from botx.clients.methods.v3.chats.create import Create
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_chat_creation_disallowed(client, requests_client):
    method = Create(
        name="test name", members=[uuid.uuid4()], chat_type=ChatTypes.group_chat,
    )

    errors_to_raise = {
        Create: (StatusCode.FORBIDDEN, ChatCreationDisallowedData(bot_id=uuid.uuid4()))
    }

    with pytest.raises(ChatCreationDisallowedError):
        with client.error_client(errors=errors_to_raise):
            await callable_to_coroutine(requests_client.call, method, "example.cts")
