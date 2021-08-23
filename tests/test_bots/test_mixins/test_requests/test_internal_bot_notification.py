import uuid

import pytest

pytestmark = pytest.mark.asyncio


async def test_internal_bot_notification(client, message):
    await client.bot.internal_bot_notification(
        credentials=message.credentials,
        group_chat_id=uuid.uuid4(),
        text="ping",
        sender=None,
        recipients=None,
        opts=None,
    )

    assert client.messages[0].data.message == "ping"
