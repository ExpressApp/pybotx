import threading

import pytest

pytestmark = pytest.mark.asyncio


async def test_register_middleware_through_decorator(
    bot, client, incoming_message, build_failed_handler, build_exception_catcher,
):
    exception_event = threading.Event()
    bot.exception_handler(Exception)(build_exception_catcher(exception_event))
    bot.default(build_failed_handler(Exception(), threading.Event()))

    await client.send_command(incoming_message)

    assert exception_event.is_set()
