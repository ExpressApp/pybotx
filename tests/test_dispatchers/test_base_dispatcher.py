import asyncio
import re

import pytest

from botx import CommandCallback, HandlersCollector, Message, Status, StatusResult
from botx.core import DEFAULT_HANDLER_BODY, BotXException
from botx.dispatchers import AsyncDispatcher
from tests.utils import re_from_str


class TestBaseDispatcher:
    @pytest.mark.asyncio
    async def test_dispatcher_status(self, handler_factory):
        collector = HandlersCollector()
        collector.handler(handler_factory("sync"), command="cmd")
        collector.hidden_command_handler(handler_factory("sync"), command="hidden")
        collector.default_handler(handler_factory("sync"))

        dispatcher = AsyncDispatcher(tasks_limit=1)
        dispatcher.add_handler(collector.handlers[re_from_str("/cmd")])
        dispatcher.add_handler(collector.handlers[re_from_str("/hidden")])
        dispatcher.add_handler(collector.handlers[DEFAULT_HANDLER_BODY])

        assert await dispatcher.status() == Status(
            result=StatusResult(
                commands=[collector.handlers[re_from_str("/cmd")].to_status_command()]
            )
        )

    @pytest.mark.asyncio
    async def test_setting_default_handler(self, message_data):
        collector = HandlersCollector()

        test_array = []

        @collector.default_handler
        def handler(*_):
            test_array.append("text")

        dispatcher = AsyncDispatcher(tasks_limit=1)
        await dispatcher.start()

        dispatcher.add_handler(collector.handlers[DEFAULT_HANDLER_BODY])
        await dispatcher.execute_command(message_data(command="text"))

        await dispatcher.shutdown()

        assert test_array

    @pytest.mark.asyncio
    async def test_registration_next_step_handlers_chains(self, message_data):
        dispatcher = AsyncDispatcher(tasks_limit=10)
        await dispatcher.start()

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

        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
        for i in range(4):
            await dispatcher.execute_command(msg)
            await asyncio.sleep(0.1)

        await dispatcher.shutdown()

        assert test_array == [i + 1 for i in range(3)]

    @pytest.mark.asyncio
    async def test_execution_by_regex_in_regex_handler(self, message_data):
        dispatcher = AsyncDispatcher(tasks_limit=1)
        await dispatcher.start()

        collector = HandlersCollector()
        msg = message_data(command="hello world")

        test_array = []

        @collector.regex_handler(command=r"hello *")
        def handler(message: Message):
            test_array.append(message.body)

        dispatcher.add_handler(collector.handlers[re.compile(r"hello *")])
        await dispatcher.execute_command(msg)

        await dispatcher.shutdown()

        assert test_array

    @pytest.mark.asyncio
    async def test_execution_by_regex_in_normal_handler(self, message_data):
        dispatcher = AsyncDispatcher(tasks_limit=1)
        await dispatcher.start()

        collector = HandlersCollector()
        msg = message_data(command="/hello world")

        test_array = []

        @collector.regex_handler(command=r"/hello")
        def handler(message: Message):
            test_array.append(message.body)

        dispatcher.add_handler(collector.handlers[re.compile(r"/hello")])
        await dispatcher.execute_command(msg)

        await dispatcher.shutdown()

        assert test_array

    @pytest.mark.asyncio
    async def test_handlers_matching_by_full_match(self, message_data, handler_factory):
        dispatcher = AsyncDispatcher(tasks_limit=1)
        await dispatcher.start()

        collector = HandlersCollector()
        msg = message_data(command="/hel world")

        collector.regex_handler(command=r"/hello")(handler_factory("sync"))

        dispatcher.add_handler(collector.handlers[re.compile(r"/hello")])

        with pytest.raises(BotXException):
            await dispatcher.execute_command(msg)

        await dispatcher.shutdown()

    @pytest.mark.asyncio
    async def test_checking_all_handlers_before_default(
        self, message_data, handler_factory
    ):
        dispatcher = AsyncDispatcher(tasks_limit=1)
        await dispatcher.start()

        collector = HandlersCollector()
        msg = message_data(command="/hello world")

        collector.regex_handler(command=r"/hell")(handler_factory("sync"))
        collector.regex_handler(command=r"/hello-world")(handler_factory("sync"))

        for handler in collector.handlers.values():
            dispatcher.add_handler(handler)

        with pytest.raises(BotXException):
            await dispatcher.execute_command(msg)

        await dispatcher.shutdown()
