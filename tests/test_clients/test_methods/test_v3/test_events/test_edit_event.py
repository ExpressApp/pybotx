import uuid

import pytest

from botx.clients.methods.v3.events.edit_event import EditEvent, UpdatePayload

pytestmark = pytest.mark.asyncio


async def test_sending_edit_event(client):
    method = EditEvent(sync_id=uuid.uuid4(), result=UpdatePayload(body="test"))

    assert await method.call(client.bot.client, "example.cts")

    assert client.requests[0].result.body == method.result.body
