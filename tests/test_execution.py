import pytest
from loguru import logger

from botx import BotXDependencyFailure, Message
from botx.execution import execute_callback_with_exception_catching

from .utils import create_callback


class TestExceptionCatcherExecution:
    @pytest.mark.asyncio
    async def test_execution_without_error(self, get_bot, message_data):
        test_array = []

        async def func():
            test_array.append(1)

        await execute_callback_with_exception_catching(
            {}, create_callback(func, Message(**message_data()), get_bot())
        )

        assert test_array

    @pytest.mark.asyncio
    async def test_passing_arguments_to_callback(self, get_bot, message_data):
        test_array = []

        async def func(arg):
            test_array.append(arg)

        await execute_callback_with_exception_catching(
            {}, create_callback(func, Message(**message_data()), get_bot(), 1)
        )

        assert test_array == [1]

    @pytest.mark.asyncio
    async def test_logging_exception_without_registered_handler(
        self, caplog, get_bot, message_data
    ):
        logger.enable("botx")

        async def func():
            raise Exception("test")

        await execute_callback_with_exception_catching(
            {}, create_callback(func, Message(**message_data()), get_bot())
        )

        assert "test" in caplog.text

    @pytest.mark.asyncio
    async def test_handling_registered_exception(self, get_bot, message_data):
        testing_array = []

        async def exc_handler(exc, *_):
            testing_array.append(exc)

        async def func():
            raise Exception("test")

        await execute_callback_with_exception_catching(
            {Exception: exc_handler},
            create_callback(func, Message(**message_data()), get_bot()),
        )

        assert testing_array[0].args == ("test",)

    @pytest.mark.asyncio
    async def test_propagating_exception_to_upper_registered(
        self, get_bot, message_data
    ):
        testing_array = []

        e = RuntimeError("test")
        m = Message(**message_data())
        b = get_bot()

        async def exc_handler(exc, msg, bot):
            testing_array.append((exc, msg, bot))

        async def func():
            raise e

        await execute_callback_with_exception_catching(
            {Exception: exc_handler}, create_callback(func, m, b)
        )

        assert testing_array[0] == (e, m, b)

    @pytest.mark.asyncio
    async def test_transformation_sync_catchers_to_coroutines(
        self, get_bot, message_data
    ):
        testing_array = []

        def exc_handler(*_):
            testing_array.append(1)

        async def func():
            raise Exception

        await execute_callback_with_exception_catching(
            {Exception: exc_handler},
            create_callback(func, Message(**message_data()), get_bot()),
        )

        assert testing_array

    @pytest.mark.asyncio
    async def test_catching_error_in_exception_catcher(self, get_bot, message_data):
        testing_array = []

        ze = ZeroDivisionError()
        re = RuntimeError()

        async def exception_handler(exc, *_):
            testing_array.append(exc)

        async def arithmetic_handler(*_):
            raise re

        async def func():
            raise ze

        await execute_callback_with_exception_catching(
            {Exception: exception_handler, ArithmeticError: arithmetic_handler},
            create_callback(func, Message(**message_data()), get_bot()),
        )

        assert testing_array == [ze, re]

    @pytest.mark.asyncio
    async def test_logging_exception_when_catcher_breaks(
        self, caplog, get_bot, message_data
    ):
        logger.enable("botx")

        ze = ZeroDivisionError()
        re = RuntimeError()

        async def arithmetic_handler(*_):
            raise re

        async def func():
            raise ze

        await execute_callback_with_exception_catching(
            {ArithmeticError: arithmetic_handler},
            create_callback(func, Message(**message_data()), get_bot()),
        )

        assert repr(ze) in caplog.text
        assert f"{repr(re)} during" in caplog.text

    @pytest.mark.asyncio
    async def test_catching_original_exception_when_catcher_is_not_coroutine(
        self, caplog, get_bot, message_data
    ):
        testing_array = []

        ze = ZeroDivisionError("zero division err")
        re = RuntimeError("runtime err")

        def exception_handler(exc, *_):
            testing_array.append(exc)

        def arithmetic_handler(*_):
            raise re

        def func():
            raise ze

        await execute_callback_with_exception_catching(
            {Exception: exception_handler, ArithmeticError: arithmetic_handler},
            create_callback(func, Message(**message_data()), get_bot()),
        )

        assert testing_array == [ze, re]

    @pytest.mark.asyncio
    async def test_doing_nothing_when_raised_dependency_error(
        self, caplog, get_bot, message_data
    ):
        logger.enable("botx")

        def func():
            raise BotXDependencyFailure

        await execute_callback_with_exception_catching(
            {}, create_callback(func, Message(**message_data()), get_bot())
        )

        assert not caplog.text
