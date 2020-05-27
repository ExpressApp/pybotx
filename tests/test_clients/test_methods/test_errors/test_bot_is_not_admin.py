import uuid

import pytest
from httpx import StatusCode

from botx.clients.methods.errors.bot_is_not_admin import (
    BotIsNotAdminData,
    BotIsNotAdminError,
)
from botx.clients.methods.v3.chats.add_user import AddUser
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_bot_is_not_admin(client, requests_client):
    method = AddUser(
        group_chat_id=uuid.uuid4(), user_huids=[uuid.uuid4() for _ in range(10)],
    )
    errors_to_raise = {
        AddUser: (
            StatusCode.FORBIDDEN,
            BotIsNotAdminData(sender=uuid.uuid4(), group_chat_id=method.group_chat_id),
        ),
    }

    with pytest.raises(BotIsNotAdminError):
        with client.error_client(errors=errors_to_raise):
            await callable_to_coroutine(requests_client.call, method, "example.cts")
