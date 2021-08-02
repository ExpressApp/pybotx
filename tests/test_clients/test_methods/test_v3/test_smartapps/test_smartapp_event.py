from typing import Any, Dict, Union
from uuid import UUID

import pytest

from botx import AsyncClient, Client, TestClient
from botx.clients.methods.v3.smartapps.smartapp_event import SmartAppEvent
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures", "tests.fixtures.smartapps")


async def test_smartapp_event(
    client: TestClient,
    requests_client: Union[AsyncClient, Client],
    ref: UUID,
    smartapp_id: UUID,
    smartapp_api_version: int,
    group_chat_id: UUID,
    smartapp_data: Dict[str, Any],
):
    method = SmartAppEvent(
        host="example.com",
        ref=ref,
        smartapp_id=smartapp_id,
        data=smartapp_data,
        smartapp_api_version=smartapp_api_version,
        group_chat_id=group_chat_id,
    )

    request = requests_client.build_request(method)
    assert await callable_to_coroutine(requests_client.execute, request)

    assert client.requests[0].ref == ref
    assert client.requests[0].smartapp_id == smartapp_id
    assert client.requests[0].smartapp_api_version == smartapp_api_version
    assert client.requests[0].group_chat_id == group_chat_id
    assert client.requests[0].data == smartapp_data
