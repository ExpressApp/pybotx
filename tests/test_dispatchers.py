import asyncio
import re

import pytest

from botx import CommandCallback, HandlersCollector, Message, Status, StatusResult
from botx.core import DEFAULT_HANDLER_BODY, BotXException
from botx.dispatchers import AsyncDispatcher, SyncDispatcher


class TestBaseDispatcher:
    def test_dispatcher_status_property(self, handler_factory):
        collector = HandlersCollector()
        collector.handler(handler_factory("sync"), command="cmd")
        collector.hidden_command_handler(handler_factory("sync"), command="hidden")
        collector.default_handler(handler_factory("sync"))

        dispatcher = SyncDispatcher(workers=1)
        dispatcher.add_handler(collector.handlers[re.compile("/cmd")])
        dispatcher.add_handler(collector.handlers[re.compile("/hidden")])
        dispatcher.add_handler(collector.handlers[DEFAULT_HANDLER_BODY])

        assert dispatcher.status == Status(
            result=StatusResult(
                commands=[collector.handlers[re.compile("/cmd")].to_status_command()]
            )
        )

    def test_setting_default_handler(self, message_data):
        collector = HandlersCollector()

        test_array = []

        @collector.default_handler
        def handler(*_):
            test_array.append("text")

        dispatcher = SyncDispatcher(workers=1)
        dispatcher.start()
        dispatcher.add_handler(collector.handlers[DEFAULT_HANDLER_BODY])
        dispatcher.execute_command(message_data(command="text"))

        dispatcher.shutdown()

        assert test_array

    def test_registration_next_step_handlers_chains(self, message_data):
        dispatcher = SyncDispatcher(workers=1)
        dispatcher.start()

        collector = HandlersCollector()

        msg = message_data(command="/handler")

        test_array = []

        @collector.handler
        def handler(message: Message):
            def ns_handler(*_):
                test_array.append(len(test_array) + 1)

            callback = CommandCallback(callback=ns_handler)

            for _ in range(3):
                dispatcher.register_next_step_handler(message, callback)

        dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        for i in range(4):
            dispatcher.execute_command(msg)

        dispatcher.shutdown()

        assert test_array == [i + 1 for i in range(3)]


class TestDispatcherAcceptableHandlers:
    def test_sync_dispatcher_accept_only_sync_functions(self, message_data):
        collector = HandlersCollector()

        @collector.handler
        async def handler(*_):
            pass

        dispatcher = SyncDispatcher(workers=1)

        with pytest.raises(BotXException):
            dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        with pytest.raises(BotXException):
            dispatcher.register_next_step_handler(
                Message(**message_data()), CommandCallback(callback=handler)
            )

    def test_async_dispatcher_accept_only_coroutines(self, message_data):
        collector = HandlersCollector()

        @collector.handler
        def handler(*_):
            pass

        dispatcher = AsyncDispatcher()

        with pytest.raises(BotXException):
            dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        with pytest.raises(BotXException):
            dispatcher.register_next_step_handler(
                Message(**message_data()), CommandCallback(callback=handler)
            )


class TestDispatchersLifespan:
    def test_sync_dispatcher_lifespan_events(self):
        dispatcher = SyncDispatcher(workers=1)
        dispatcher.start()
        dispatcher.shutdown()

    @pytest.mark.asyncio
    async def test_async_dispatcher_lifespan_events(self):
        dispatcher = AsyncDispatcher()
        await dispatcher.start()
        await dispatcher.shutdown()


class TestSyncDispatcherHandlersExecution:
    def test_raising_exception_when_missing_handler_call(self, message_data):
        dispatcher = SyncDispatcher(workers=1)
        dispatcher.start()

        with pytest.raises(BotXException):
            dispatcher.execute_command(message_data(command="/handler"))

        dispatcher.shutdown()

    def test_executing_handlers_for_commands(self, message_data):
        collector = HandlersCollector()

        testing_array = []

        @collector.handler
        def handler(*_):
            testing_array.append("text")

        dispatcher = SyncDispatcher(workers=1)
        dispatcher.start()
        dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        dispatcher.execute_command(message_data(command="/handler"))
        dispatcher.shutdown()

        assert testing_array

    def test_next_step_handlers_registration(self, message_data):
        dispatcher = SyncDispatcher(workers=1)
        dispatcher.start()

        collector = HandlersCollector()

        msg = message_data(command="/handler")

        testing_array = []

        @collector.handler
        def handler(message: Message, *_):
            def ns_handler(*_):
                testing_array.append(2)

            testing_array.append(1)
            dispatcher.register_next_step_handler(
                message, CommandCallback(callback=ns_handler)
            )

        dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        dispatcher.execute_command(msg)

        assert testing_array

        dispatcher.execute_command(msg)
        dispatcher.shutdown()

        assert len(testing_array) == 2

    def test_passing_extra_arguments_into_next_step_handlers(self, message_data):
        dispatcher = SyncDispatcher(workers=1)
        dispatcher.start()

        collector = HandlersCollector()

        msg = message_data(command="/handler")
        args = (1, True)
        kwargs = dict(kwarg1="test", kwarg2=1.23)

        testing_array = []

        @collector.handler
        def handler(message: Message):
            def ns_handler(_, arg1: int, arg2: bool, *, kwarg1: str, kwarg2: float):
                testing_array.extend([(arg1, arg2), dict(kwarg1=kwarg1, kwarg2=kwarg2)])

            testing_array.append(1)
            dispatcher.register_next_step_handler(
                message, CommandCallback(callback=ns_handler, args=args, kwargs=kwargs)
            )

        dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        dispatcher.execute_command(msg)

        assert testing_array

        dispatcher.execute_command(msg)
        dispatcher.shutdown()

        assert testing_array[1:] == [args, kwargs]

    def test_allowing_extra_arguments_for_common_handlers(self, message_data):
        dispatcher = SyncDispatcher(workers=1)
        dispatcher.start()

        collector = HandlersCollector()
        args = (1, True)
        kwargs = dict(kwarg1="test", kwarg2=1.23)

        testing_array = []

        @collector.handler
        def handler(
            _,
            arg1: int = 1,
            arg2: bool = True,
            *,
            kwarg1: str = "test",
            kwarg2: float = 1.23
        ):
            testing_array.extend([(arg1, arg2), dict(kwarg1=kwarg1, kwarg2=kwarg2)])

        dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        dispatcher.execute_command(message_data(command="/handler"))

        assert testing_array == [args, kwargs]

        dispatcher.shutdown()

    def test_calling_common_handlers_from_next_step_handler(self, message_data):
        dispatcher = SyncDispatcher(workers=1)
        dispatcher.start()
        msg = message_data(command="/handler")

        collector = HandlersCollector()
        args = (1, True)
        kwargs = dict(kwarg1="test", kwarg2=1.23)

        testing_array = []

        @collector.handler
        def second_handler(
            _,
            arg1: int = 1,
            arg2: bool = True,
            *,
            kwarg1: str = "test",
            kwarg2: float = 1.23
        ):
            testing_array.extend([(arg1, arg2), dict(kwarg1=kwarg1, kwarg2=kwarg2)])

        @collector.handler
        def handler(message: Message):
            dispatcher.register_next_step_handler(
                message,
                CommandCallback(callback=second_handler, args=args, kwargs=kwargs),
            )

        dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        dispatcher.execute_command(msg)

        dispatcher.execute_command(msg)

        dispatcher.shutdown()

        assert testing_array == [args, kwargs]


class TestAsyncDispatcherHandlersExecution:
    @pytest.mark.asyncio
    async def test_raising_exception_when_missing_handler_call(self, message_data):
        dispatcher = AsyncDispatcher()
        await dispatcher.start()

        with pytest.raises(BotXException):
            await dispatcher.execute_command(message_data(command="/handler"))

        await dispatcher.shutdown()

    @pytest.mark.asyncio
    async def test_executing_handlers_for_commands(self, message_data):
        collector = HandlersCollector()

        testing_array = []

        @collector.handler
        async def handler(*_):
            testing_array.append("text")

        dispatcher = AsyncDispatcher()
        await dispatcher.start()
        dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        await dispatcher.execute_command(message_data(command="/handler"))
        await dispatcher.shutdown()

        assert testing_array

    @pytest.mark.asyncio
    async def test_next_step_handlers_registration(self, message_data):
        dispatcher = AsyncDispatcher()
        await dispatcher.start()

        collector = HandlersCollector()

        msg = message_data(command="/handler")

        testing_array = []

        @collector.handler
        async def handler(message: Message, *_):
            async def ns_handler(*_):
                testing_array.append(2)

            testing_array.append(1)
            dispatcher.register_next_step_handler(
                message, CommandCallback(callback=ns_handler)
            )

        dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        await dispatcher.execute_command(msg)

        await asyncio.sleep(0.1)
        assert testing_array

        await dispatcher.execute_command(msg)
        await dispatcher.shutdown()

        assert len(testing_array) == 2

    @pytest.mark.asyncio
    async def test_passing_extra_arguments_into_next_step_handlers(self, message_data):
        dispatcher = AsyncDispatcher()
        await dispatcher.start()

        collector = HandlersCollector()

        msg = message_data(command="/handler")
        args = (1, True)
        kwargs = dict(kwarg1="test", kwarg2=1.23)

        testing_array = []

        @collector.handler
        async def handler(message: Message):
            async def ns_handler(
                _, arg1: int, arg2: bool, *, kwarg1: str, kwarg2: float
            ):
                testing_array.extend([(arg1, arg2), dict(kwarg1=kwarg1, kwarg2=kwarg2)])

            testing_array.append(1)
            dispatcher.register_next_step_handler(
                message, CommandCallback(callback=ns_handler, args=args, kwargs=kwargs)
            )

        dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        await dispatcher.execute_command(msg)

        await asyncio.sleep(0.1)
        assert testing_array

        await dispatcher.execute_command(msg)
        await dispatcher.shutdown()

        assert testing_array[1:] == [args, kwargs]

    @pytest.mark.asyncio
    async def test_allowing_extra_arguments_for_common_handlers(self, message_data):
        dispatcher = AsyncDispatcher()
        await dispatcher.start()

        collector = HandlersCollector()
        args = (1, True)
        kwargs = dict(kwarg1="test", kwarg2=1.23)

        testing_array = []

        @collector.handler
        async def handler(
            _,
            arg1: int = 1,
            arg2: bool = True,
            *,
            kwarg1: str = "test",
            kwarg2: float = 1.23
        ):
            testing_array.extend([(arg1, arg2), dict(kwarg1=kwarg1, kwarg2=kwarg2)])

        dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        await dispatcher.execute_command(message_data(command="/handler"))

        await asyncio.sleep(0.1)
        assert testing_array == [args, kwargs]

        await dispatcher.shutdown()

    @pytest.mark.asyncio
    async def test_calling_common_handlers_from_next_step_handler(self, message_data):
        dispatcher = AsyncDispatcher()
        await dispatcher.start()
        msg = message_data(command="/handler")

        collector = HandlersCollector()
        args = (1, True)
        kwargs = dict(kwarg1="test", kwarg2=1.23)

        testing_array = []

        @collector.handler
        async def second_handler(
            _,
            arg1: int = 1,
            arg2: bool = True,
            *,
            kwarg1: str = "test",
            kwarg2: float = 1.23
        ):
            testing_array.extend([(arg1, arg2), dict(kwarg1=kwarg1, kwarg2=kwarg2)])

        @collector.handler
        async def handler(message: Message):
            dispatcher.register_next_step_handler(
                message,
                CommandCallback(callback=second_handler, args=args, kwargs=kwargs),
            )

        dispatcher.add_handler(collector.handlers[re.compile("/handler")])
        await dispatcher.execute_command(msg)
        await asyncio.sleep(0.1)
        await dispatcher.execute_command(msg)
        await asyncio.sleep(0.1)

        await dispatcher.shutdown()

        assert testing_array == [args, kwargs]
