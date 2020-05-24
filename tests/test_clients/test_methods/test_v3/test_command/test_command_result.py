import uuid

import pytest

from botx.clients.methods.v3.command.command_result import CommandResult
from botx.clients.types.result_payload import ResultPayload

pytestmark = pytest.mark.asyncio


async def test_sending_command_result(client):
    method = CommandResult(
        sync_id=uuid.uuid4(), bot_id=uuid.uuid4(), result=ResultPayload(body="test")
    )

    assert await method.call(client.bot.client, "example.cts")

    assert client.requests[0].result.body == method.result.body
