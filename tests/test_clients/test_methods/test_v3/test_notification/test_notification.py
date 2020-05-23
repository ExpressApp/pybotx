import uuid

import pytest

from botx.clients.methods.v3.notification.notification import Notification
from botx.clients.types.result_payload import ResultPayload

pytestmark = pytest.mark.asyncio


async def test_sending_notification(client):
    method = Notification(
        group_chat_ids=[uuid.uuid4()],
        bot_id=uuid.uuid4(),
        result=ResultPayload(body="test"),
    )
    method.fill_credentials("example.cts", "")

    assert await method.call(client.bot.client)

    assert client.requests[0].result.body == method.result.body
