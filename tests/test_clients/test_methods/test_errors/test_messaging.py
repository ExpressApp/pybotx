import uuid

import pytest
from httpx import StatusCode

from botx.clients.methods.errors.messaging import MessagingError
from botx.clients.methods.v3.chats.info import Info
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_messaging_error(client, requests_client):
    method = Info(group_chat_id=uuid.uuid4())

    errors_to_raise = {Info: (StatusCode.BAD_REQUEST, {})}

    with client.error_client(errors=errors_to_raise):
        with pytest.raises(MessagingError):
            await callable_to_coroutine(requests_client.call, method, "example.cts")
