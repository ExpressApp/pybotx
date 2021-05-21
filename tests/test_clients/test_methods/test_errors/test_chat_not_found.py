import uuid
from http import HTTPStatus

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
    method = AddUser(
        host="example.com",
        group_chat_id=uuid.uuid4(),
        user_huids=[uuid.uuid4()],
    )

    errors_to_raise = {
        AddUser: (
            HTTPStatus.NOT_FOUND,
            ChatNotFoundData(group_chat_id=method.group_chat_id),
        ),
    }

    with client.error_client(errors=errors_to_raise):
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, request)

        with pytest.raises(ChatNotFoundError):
            await callable_to_coroutine(
                requests_client.process_response,
                method,
                response,
            )
