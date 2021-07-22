import uuid
from http import HTTPStatus

import pytest

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
        host="example.com",
        name="test name",
        members=[uuid.uuid4()],
        chat_type=ChatTypes.group_chat,
        shared_history=False,
    )

    errors_to_raise = {
        Create: (
            HTTPStatus.FORBIDDEN,
            ChatCreationDisallowedData(bot_id=uuid.uuid4()),
        ),
    }

    with client.error_client(errors=errors_to_raise):
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, request)

        with pytest.raises(ChatCreationDisallowedError):
            await callable_to_coroutine(
                requests_client.process_response,
                method,
                response,
            )
