import uuid

import pytest
from httpx import StatusCode

from botx.clients.methods.errors.messaging import MessagingError
from botx.clients.methods.v3.chats.info import Info

pytestmark = pytest.mark.asyncio


async def test_raising_messaging_error(client):
    method = Info(group_chat_id=uuid.uuid4())

    errors_to_raise = {Info: (StatusCode.BAD_REQUEST, {})}

    with pytest.raises(MessagingError):
        with client.error_client(errors=errors_to_raise):
            await method.call(client.bot.client, "example.cts")
