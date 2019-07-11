import pytest

from botx import CommandCallback, HandlersCollector, Message
from botx.core import BotXException
from botx.dispatchers import SyncDispatcher
from tests.utils import re_from_str


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
        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
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

        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
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

        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
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

        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
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

        dispatcher.add_handler(collector.handlers[re_from_str("/handler")])
        dispatcher.execute_command(msg)

        dispatcher.execute_command(msg)

        dispatcher.shutdown()

        assert testing_array == [args, kwargs]
