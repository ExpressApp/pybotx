import uuid

import pytest

from botx.clients.methods.v3.notification.notification import Notification
from botx.clients.types.message_payload import ResultPayload
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_sending_notification(client, requests_client):
    method = Notification(
        group_chat_ids=[uuid.uuid4()],
        bot_id=uuid.uuid4(),
        result=ResultPayload(body="test"),
    )

    assert await callable_to_coroutine(requests_client.call, method, "example.cts")

    assert client.requests[0].result.body == method.result.body
