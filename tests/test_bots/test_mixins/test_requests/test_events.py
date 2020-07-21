import pytest

from botx import UpdatePayload

pytestmark = pytest.mark.asyncio


async def test_updating_message_through_bot(bot, client, message):
    sync_id = await bot.answer_message("some text", message)

    await bot.update_message(
        message.credentials.copy(update={"sync_id": sync_id}),
        UpdatePayload(text="new text"),
    )

    update = client.message_updates[0].result
    assert update.body == "new text"


async def test_cant_update_without_sync_id(bot, client, message):
    credentials = message.credentials.copy(update={"sync_id": None})

    with pytest.raises(ValueError) as exc:
        await bot.update_message(credentials, UpdatePayload(text="new text"))

    assert "sync_id is required" in str(exc.value)
