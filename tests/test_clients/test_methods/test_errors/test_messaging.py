import uuid
from http import HTTPStatus

import pytest

from botx.clients.methods.errors.messaging import MessagingError
from botx.clients.methods.v3.chats.info import Info
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_messaging_error(client, requests_client):
    method = Info(group_chat_id=uuid.uuid4())

    errors_to_raise = {Info: (HTTPStatus.BAD_REQUEST, {})}

    with client.error_client(errors=errors_to_raise):
        method.host = "example.com"
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, method, request)

        with pytest.raises(MessagingError):
            await callable_to_coroutine(
                requests_client.process_response, method, response,
            )
