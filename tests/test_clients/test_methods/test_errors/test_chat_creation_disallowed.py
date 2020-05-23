import uuid

import pytest
from httpx import StatusCode

from botx import ChatTypes
from botx.clients.methods.errors.chat_creation_disallowed import (
    ChatCreationDisallowedData,
    ChatCreationDisallowedError,
)
from botx.clients.methods.v3.chats.create import Create

pytestmark = pytest.mark.asyncio


async def test_raising_chat_creation_disallowed(client):
    method = Create(
        name="test name", members=[uuid.uuid4()], chat_type=ChatTypes.group_chat,
    )
    method.fill_credentials("example.cts", "")

    errors_to_raise = {
        Create: (StatusCode.FORBIDDEN, ChatCreationDisallowedData(bot_id=uuid.uuid4()),)
    }

    with pytest.raises(ChatCreationDisallowedError):
        with client.error_client(errors=errors_to_raise):
            await method.call(client.bot.client)
