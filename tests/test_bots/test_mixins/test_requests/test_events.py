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


async def test_reply(bot, client, message):
    await bot.reply(
        text="foo",
        source_sync_id=message.sync_id,
        credentials=message.credentials,
    )

    reply = client.replies[0]
    assert reply.result.body == "foo"
    assert reply.source_sync_id == message.sync_id


async def test_reply_on_message_empty_text_error(bot, message):
    with pytest.raises(ValueError):
        await bot.reply(
            text="",
            source_sync_id=message.sync_id,
            credentials=message.credentials,
        )


async def test_reply_arguments_error(bot, message):
    with pytest.raises(ValueError):
        await bot.reply(
            source_sync_id=message.sync_id,
            credentials=message.credentials,
        )
