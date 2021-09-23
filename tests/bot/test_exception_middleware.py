import logging
from typing import Any, Callable, Generator
from unittest.mock import MagicMock, call

import pytest
from loguru import logger

from botx import Bot, HandlerCollector, IncomingMessage, lifespan_wrapper


class AsyncMock(MagicMock):
    async def __call__(self, *args: Any, **kwargs: Any) -> Any:  # noqa: WPS612
        return super().__call__(*args, **kwargs)


@pytest.fixture
def async_mock() -> AsyncMock:
    return AsyncMock(__bool__=lambda self: True)  # noqa: WPS117


@pytest.fixture()
def loguru_caplog(
    caplog: pytest.LogCaptureFixture,
) -> Generator[pytest.LogCaptureFixture, None, None]:
    # https://github.com/Delgan/loguru/issues/59

    class PropogateHandler(logging.Handler):  # noqa: WPS431
        def emit(self, record: logging.LogRecord) -> None:
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message}")
    yield caplog
    logger.remove(handler_id)


@pytest.mark.asyncio
async def test_exception_middleware_with_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    async_mock: AsyncMock,
) -> None:
    # - Arrange -
    exc = ValueError("test_error")
    value_error_handler = async_mock

    user_command = incoming_message_factory(body="/command")

    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        raise exc

    built_bot = Bot(collectors=[collector])
    built_bot.add_exception_handler(ValueError, value_error_handler)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert len(value_error_handler.mock_calls) == 1
    assert value_error_handler.mock_calls[0] == call(exc, user_command, built_bot)


@pytest.mark.asyncio
async def test_exception_middleware_without_handler(
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")

    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        raise ValueError("Testing exception middleware")

    built_bot = Bot(collectors=[collector])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert "Uncaught exception ValueError" in loguru_caplog.text
    assert "Testing exception middleware" in loguru_caplog.text


@pytest.mark.asyncio
async def test_exception_middleware_with_handler_error(
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")

    async def exception_handler(
        exc: Exception,
        message: IncomingMessage,
        bot: Bot,
    ) -> None:
        raise ValueError("Nested error")

    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        raise ValueError("Testing exception middleware")

    built_bot = Bot(collectors=[collector])
    built_bot.add_exception_handler(Exception, exception_handler)

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert "Uncaught exception ValueError in exception handler" in loguru_caplog.text
    assert "Testing exception middleware" in loguru_caplog.text
    assert "Nested error" in loguru_caplog.text
