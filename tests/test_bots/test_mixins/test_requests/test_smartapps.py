from typing import Any, Dict
from uuid import UUID

import pytest

from botx import Message, TestClient
from botx.clients.methods.v3.smartapps.smartapp_event import SmartAppEvent
from botx.clients.methods.v3.smartapps.smartapp_notification import SmartAppNotification
from botx.models.smartapps import SendingSmartAppEvent

pytestmark = pytest.mark.asyncio
pytest_plugins = ("tests.test_clients.fixtures", "tests.fixtures.smartapps")


async def test_smartapp_event(
    client: TestClient,
    message: Message,
    ref: UUID,
    smartapp_id: UUID,
    smartapp_api_version: int,
    group_chat_id: UUID,
    smartapp_data: Dict[str, Any],
):
    await client.bot.send_smartapp_event(
        credentials=message.credentials,
        smartapp_event=SendingSmartAppEvent(
            ref=ref,
            smartapp_id=smartapp_id,
            smartapp_api_version=smartapp_api_version,
            group_chat_id=group_chat_id,
            data=smartapp_data,
        ),
    )

    assert client.requests[0] == SmartAppEvent(
        ref=ref,
        smartapp_id=smartapp_id,
        smartapp_api_version=smartapp_api_version,
        group_chat_id=group_chat_id,
        data=smartapp_data,
    )


async def test_smartapp_notification(
    client: TestClient,
    message: Message,
    smartapp_api_version: int,
    group_chat_id: UUID,
    smartapp_counter: int,
):
    await client.bot.send_smartapp_notification(
        credentials=message.credentials,
        smartapp_notification=SmartAppNotification(
            smartapp_api_version=smartapp_api_version,
            group_chat_id=group_chat_id,
            smartapp_counter=smartapp_counter,
        ),
    )

    assert client.requests[0] == SmartAppNotification(
        smartapp_api_version=smartapp_api_version,
        group_chat_id=group_chat_id,
        smartapp_counter=smartapp_counter,
    )
