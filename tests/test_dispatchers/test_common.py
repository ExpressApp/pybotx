import pytest

from botx import CommandCallback, HandlersCollector, Message
from botx.dispatchers import AsyncDispatcher, SyncDispatcher
from tests.utils import re_from_str


class TestDispatcherAcceptableHandlers:
    def test_sync_dispatcher_accept_async_functions(self, message_data):
        collector = HandlersCollector()

        @collector.handler
        async def handler(*_):
            pass

        dispatcher = SyncDispatcher(workers=1)

        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
        dispatcher.register_next_step_handler(
            Message(**message_data()), CommandCallback(callback=handler)
        )

    def test_sync_dispatcher_can_execute_async_handlers(self, message_data):
        collector = HandlersCollector()

        testing_array = []

        @collector.handler
        async def handler(*_):
            testing_array.append(True)

        dispatcher = SyncDispatcher(workers=1)

        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])

        dispatcher.start()
        dispatcher.execute_command(message_data("/handler"))
        dispatcher.shutdown()

        assert testing_array

    def test_async_dispatcher_accept_not_only_coroutines(self, message_data):
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
    async def test_async_dispatcher_can_execute_sync_handlers(self, message_data):
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


class TestDispatchersLifespan:
    def test_sync_dispatcher_lifespan_events(self):
        dispatcher = SyncDispatcher(workers=1)
        dispatcher.start()
        dispatcher.shutdown()

    @pytest.mark.asyncio
    async def test_async_dispatcher_lifespan_events(self):
        dispatcher = AsyncDispatcher(tasks_limit=10)
        await dispatcher.start()
        await dispatcher.shutdown()
