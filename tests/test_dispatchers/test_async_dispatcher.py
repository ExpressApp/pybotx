import asyncio

import pytest

from botx import CommandCallback, HandlersCollector, Message
from botx.core import BotXException
from botx.dispatchers import AsyncDispatcher
from tests.utils import re_from_str


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
        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
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

        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
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

        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
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

        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
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

        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
        await dispatcher.execute_command(msg)
        await asyncio.sleep(0.1)
        await dispatcher.execute_command(msg)
        await asyncio.sleep(0.1)

        await dispatcher.shutdown()

        assert testing_array == [args, kwargs]
