import threading

import pytest

from botx import TestClient

pytestmark = pytest.mark.asyncio


async def test_disabling_sync_send_for_client(bot, incoming_message, build_handler):
    bot.default(build_handler(threading.Event()))

    with TestClient(bot) as client:
        await client.send_command(incoming_message, False)

        assert bot.tasks

    await bot.shutdown()

    assert not bot.tasks
