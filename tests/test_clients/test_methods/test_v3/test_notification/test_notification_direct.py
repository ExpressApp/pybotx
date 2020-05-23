import uuid

import pytest

from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.types.result_payload import ResultPayload

pytestmark = pytest.mark.asyncio


async def test_sending_direct_notification(client):
    method = NotificationDirect(
        group_chat_id=uuid.uuid4(),
        bot_id=uuid.uuid4(),
        result=ResultPayload(body="test"),
    )
    method.fill_credentials("example.cts", "")

    assert await method.call(client.bot.client)

    assert client.requests[0].result.body == method.result.body
