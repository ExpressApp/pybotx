import threading

import pytest

from botx import Collector, Depends

pytestmark = pytest.mark.asyncio


async def test_dependencies_from_bot_on_default_handler(
    bot, incoming_message, client, build_handler
):
    event1 = threading.Event()
    event2 = threading.Event()

    bot.collector = bot.exception_middleware.executor = Collector(
        dependencies=[Depends(build_handler(event1))]
    )

    bot.default(build_handler(event2))

    await client.send_command(incoming_message)

    assert event1.is_set()
    assert event2.is_set()


async def test_dependency_saved_after_include_collector(
    bot, incoming_message, client, build_handler
):
    event1 = threading.Event()
    event2 = threading.Event()

    collector = Collector()
    collector.default(build_handler(event1))

    bot.collector = bot.exception_middleware.executor = Collector(
        dependencies=[Depends(build_handler(event2))]
    )
    bot.include_collector(collector)

    await client.send_command(incoming_message)

    assert event1.is_set()
    assert event2.is_set()
