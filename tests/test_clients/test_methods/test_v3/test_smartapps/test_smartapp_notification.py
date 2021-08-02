from typing import Union
from uuid import UUID

import pytest

from botx import AsyncClient, Client, TestClient
from botx.clients.methods.v3.smartapps.smartapp_notification import SmartAppNotification
from botx.concurrency import callable_to_coroutine

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures", "tests.fixtures.smartapps")


async def test_smartapp_event(
    client: TestClient,
    requests_client: Union[AsyncClient, Client],
    smartapp_api_version: int,
    group_chat_id: UUID,
    smartapp_counter: int,
) -> None:
    method = SmartAppNotification(
        host="example.com",
        group_chat_id=group_chat_id,
        smartapp_counter=smartapp_counter,
        smartapp_api_version=smartapp_api_version,
    )

    request = requests_client.build_request(method)
    assert await callable_to_coroutine(requests_client.execute, request)

    assert client.requests[0].smartapp_counter == smartapp_counter
    assert client.requests[0].smartapp_api_version == smartapp_api_version
    assert client.requests[0].group_chat_id == group_chat_id
