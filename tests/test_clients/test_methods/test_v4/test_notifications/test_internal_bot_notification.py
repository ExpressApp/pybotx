import uuid

import pytest

from botx.clients.methods.v4.notifications.internal_bot_notification import (
    InternalBotNotification,
)
from botx.clients.types.message_payload import InternalBotNotificationPayload
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_sending_internal_bot_notification(client, requests_client):
    method = InternalBotNotification(
        host="example.com",
        group_chat_id=uuid.uuid4(),
        bot_id=uuid.uuid4(),
        data=InternalBotNotificationPayload(message="test"),
    )

    request = requests_client.build_request(method)
    assert await callable_to_coroutine(requests_client.execute, request)

    assert client.requests[0].data.message == "test"
