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
) -> None:
    method = SmartAppEvent(
        host="example.com",  # type: ignore [call-arg]
        ref=ref,
        smartapp_id=smartapp_id,
        data=smartapp_data,
        smartapp_api_version=smartapp_api_version,
        group_chat_id=group_chat_id,
    )

    request = requests_client.build_request(method)
    assert await callable_to_coroutine(requests_client.execute, request)

    assert isinstance(client.requests[0], SmartAppEvent)
    smartapp_event = client.requests[0]

    assert smartapp_event.ref == ref
    assert smartapp_event.smartapp_id == smartapp_id
    assert smartapp_event.smartapp_api_version == smartapp_api_version
    assert smartapp_event.group_chat_id == group_chat_id
    assert smartapp_event.data == smartapp_data
