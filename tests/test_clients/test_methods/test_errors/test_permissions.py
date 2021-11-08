import uuid
from http import HTTPStatus

import pytest

from botx.clients.methods.errors.permissions import (
    NoPermissionError,
    NoPermissionErrorData,
)
from botx.clients.methods.v3.chats.pin_message import PinMessage
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_raising_no_permission(client, requests_client):
    method = PinMessage(
        host="example.com",
        chat_id=uuid.uuid4(),
        sync_id=uuid.uuid4(),
    )

    errors_to_raise = {
        PinMessage: (
            HTTPStatus.FORBIDDEN,
            NoPermissionErrorData(group_chat_id=method.chat_id),
        ),
    }

    with client.error_client(errors=errors_to_raise):
        request = requests_client.build_request(method)
        response = await callable_to_coroutine(requests_client.execute, request)

        with pytest.raises(NoPermissionError):
            await callable_to_coroutine(
                requests_client.process_response,
                method,
                response,
            )
