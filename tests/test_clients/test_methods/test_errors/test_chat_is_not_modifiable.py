import uuid

import pytest
from httpx import StatusCode

from botx.clients.methods.errors.chat_is_not_modifiable import (
    PersonalChatIsNotModifiableData,
    PersonalChatIsNotModifiableError,
)
from botx.clients.methods.v3.chats.add_user import AddUser

pytestmark = pytest.mark.asyncio


async def test_raising_chat_is_not_modifiable(client):
    method = AddUser(group_chat_id=uuid.uuid4(), user_huids=[uuid.uuid4()])

    errors_to_raise = {
        AddUser: (
            StatusCode.FORBIDDEN,
            PersonalChatIsNotModifiableData(group_chat_id=method.group_chat_id),
        )
    }

    with pytest.raises(PersonalChatIsNotModifiableError):
        with client.error_client(errors=errors_to_raise):
            await method.call(client.bot.client, "example.cts")
