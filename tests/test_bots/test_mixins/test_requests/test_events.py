import pytest

from botx import UpdatePayload

pytestmark = pytest.mark.asyncio


async def test_updating_message_through_bot(bot, client, message):
    sync_id = await bot.answer_message("some text", message,)

    await bot.update_message(
        message.credentials.copy(update={"sync_id": sync_id}),
        UpdatePayload(text="new text"),
    )

    update = client.message_updates[0].result
    assert update.body == "new text"
