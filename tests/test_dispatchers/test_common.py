import pytest

from botx import CommandCallback, HandlersCollector, Message
from botx.dispatchers import AsyncDispatcher
from tests.utils import re_from_str


def test_async_dispatcher_accept_not_only_coroutines(message_data):
    collector = HandlersCollector()

    @collector.handler
    def handler(*_):
        pass

    dispatcher = AsyncDispatcher(tasks_limit=10)

    dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
    dispatcher.register_next_step_handler(
        Message(**message_data()), CommandCallback(callback=handler)
    )


@pytest.mark.asyncio
async def test_async_dispatcher_can_execute_sync_handlers(message_data):
    collector = HandlersCollector()

    testing_array = []

    @collector.handler
    def handler(*_):
        testing_array.append(True)

    dispatcher = AsyncDispatcher(tasks_limit=10)

    dispatcher.add_handler(collector.handlers[re_from_str("/handler")])

    await dispatcher.start()
    await dispatcher.execute_command(message_data("/handler"))
    await dispatcher.shutdown()

    assert testing_array


@pytest.mark.asyncio
async def test_async_dispatcher_lifespan_events():
    dispatcher = AsyncDispatcher(tasks_limit=10)
    await dispatcher.start()
    await dispatcher.shutdown()
