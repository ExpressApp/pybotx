import threading

import pytest

pytestmark = pytest.mark.asyncio


async def test_bot_process_message_by_sorted_handlers(
    bot, client, incoming_message, build_handler,
):
    event1 = threading.Event()
    event2 = threading.Event()

    bot.handler(build_handler(event1), command="/body")
    bot.handler(build_handler(event2), command="/body-v2")

    incoming_message.command.body = "/body-v2 args"
    await client.send_command(incoming_message)

    assert not event1.is_set()
    assert event2.is_set()
