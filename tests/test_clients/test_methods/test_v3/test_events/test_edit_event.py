import uuid

import pytest

from botx.clients.methods.v3.events.edit_event import EditEvent
from botx.clients.types.message_payload import UpdatePayload
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures",)


async def test_sending_edit_event(client, requests_client):
    method = EditEvent(sync_id=uuid.uuid4(), result=UpdatePayload(body="test"))

    method.host = "example.com"
    request = requests_client.build_request(method)
    assert await callable_to_coroutine(requests_client.execute, method, request)

    assert client.requests[0].result.body == method.result.body
