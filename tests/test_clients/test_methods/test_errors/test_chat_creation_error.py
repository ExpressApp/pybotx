import uuid

import pytest
from httpx import StatusCode

from botx import ChatTypes
from botx.clients.methods.errors.chat_creation_error import ChatCreationError
from botx.clients.methods.v3.chats.create import Create

pytestmark = pytest.mark.asyncio


async def test_raising_chat_creation_error(client):
    method = Create(
        name="test name", members=[uuid.uuid4()], chat_type=ChatTypes.group_chat,
    )

    errors_to_raise = {Create: (StatusCode.UNPROCESSABLE_ENTITY, {})}

    with pytest.raises(ChatCreationError):
        with client.error_client(errors=errors_to_raise):
            await method.call(client.bot.client, "example.cts")
