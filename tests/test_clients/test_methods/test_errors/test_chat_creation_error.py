import uuid

import httpx
import pytest

from botx import ChatTypes
from botx.clients.methods.errors.chat_creation_error import ChatCreationError
from botx.clients.methods.v3.chats.create import Create
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_chat_creation_error(client, requests_client):
    method = Create(
        name="test name", members=[uuid.uuid4()], chat_type=ChatTypes.group_chat,
    )

    errors_to_raise = {Create: (httpx.codes.UNPROCESSABLE_ENTITY, {})}

    with client.error_client(errors=errors_to_raise):
        with pytest.raises(ChatCreationError):
            await callable_to_coroutine(requests_client.call, method, "example.cts")
