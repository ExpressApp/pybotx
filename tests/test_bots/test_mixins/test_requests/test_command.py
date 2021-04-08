import pytest

from botx import MessagePayload

pytestmark = pytest.mark.asyncio


async def test_command_result(client, message):
    await client.bot.send_command_result(
        credentials=message.credentials,
        payload=MessagePayload(text="some text"),
    )

    assert client.command_results[0].result.body == "some text"
