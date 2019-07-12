import pytest
from loguru import logger

from botx.execution import execute_callback_with_exception_catching

from .utils import create_callback


class TestExceptionCatcherExecution:
    @pytest.mark.asyncio
    async def test_execution_without_error(self):
        test_array = []

        async def func():
            test_array.append(1)

        await execute_callback_with_exception_catching({}, create_callback(func))

        assert test_array

    @pytest.mark.asyncio
    async def test_passing_arguments_to_callback(self):
        test_array = []

        async def func(arg):
            test_array.append(arg)

        await execute_callback_with_exception_catching({}, create_callback(func, 1))

        assert test_array == [1]

    @pytest.mark.asyncio
    async def test_logging_exception_without_registered_handler(self, caplog):
        logger.enable("botx")

        async def func():
            raise Exception("test")

        await execute_callback_with_exception_catching({}, create_callback(func))

        assert "test" in caplog.text

    @pytest.mark.asyncio
    async def test_handling_registered_exception(self):
        testing_array = []

        async def exc_handler(exc):
            testing_array.append(exc)

        async def func():
            raise Exception("test")

        await execute_callback_with_exception_catching(
            {Exception: exc_handler}, create_callback(func)
        )

        assert testing_array[0].args == ("test",)

    @pytest.mark.asyncio
    async def test_passing_original_arguments_to_exception_handler(self):
        testing_array = []

        e = Exception("test")

        async def exc_handler(exc, arg):
            testing_array.append((exc, arg))

        async def func(_):
            raise e

        await execute_callback_with_exception_catching(
            {Exception: exc_handler}, create_callback(func, 1)
        )

        assert testing_array[0] == (e, 1)

    @pytest.mark.asyncio
    async def test_propagating_exception_to_upper_registered(self):
        testing_array = []

        e = RuntimeError("test")

        async def exc_handler(exc, arg):
            testing_array.append((exc, arg))

        async def func(_):
            raise e

        await execute_callback_with_exception_catching(
            {Exception: exc_handler}, create_callback(func, 1)
        )

        assert testing_array[0] == (e, 1)

    @pytest.mark.asyncio
    async def test_transformation_sync_catchers_to_coroutines(self):
        testing_array = []

        def exc_handler(_):
            testing_array.append(1)

        async def func():
            raise Exception

        await execute_callback_with_exception_catching(
            {Exception: exc_handler}, create_callback(func)
        )

        assert testing_array

    @pytest.mark.asyncio
    async def test_catching_error_in_exception_catcher(self):
        testing_array = []

        ze = ZeroDivisionError()
        re = RuntimeError()

        async def exception_handler(exc):
            testing_array.append(exc)

        async def arithmetic_handler(exc):
            raise re

        async def func():
            raise ze

        await execute_callback_with_exception_catching(
            {Exception: exception_handler, ArithmeticError: arithmetic_handler},
            create_callback(func),
        )

        assert testing_array == [ze, re]

    @pytest.mark.asyncio
    async def test_logging_exception_when_catcher_breaks(self, caplog):
        logger.enable("botx")

        ze = ZeroDivisionError()
        re = RuntimeError()

        async def arithmetic_handler(_):
            raise re

        async def func():
            raise ze

        await execute_callback_with_exception_catching(
            {ArithmeticError: arithmetic_handler}, create_callback(func)
        )

        assert repr(ze) in caplog.text
        assert f"{repr(re)} during" in caplog.text

    @pytest.mark.asyncio
    async def test_catching_original_exception_when_catcher_is_not_coroutine(
        self, caplog
    ):
        testing_array = []

        ze = ZeroDivisionError("zero division err")
        re = RuntimeError("runtime err")

        def exception_handler(exc):
            testing_array.append(exc)

        def arithmetic_handler(exc):
            raise re

        def func():
            raise ze

        await execute_callback_with_exception_catching(
            {Exception: exception_handler, ArithmeticError: arithmetic_handler},
            create_callback(func),
        )

        assert testing_array == [ze, re]
