import asyncio
from typing import Callable
from unittest.mock import MagicMock, call

import pytest

from pybotx import (
    Bot,
    BotAccountWithSecret,
    HandlerCollector,
    IncomingMessage,
    lifespan_wrapper,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.mock_authorization,
    pytest.mark.usefixtures("respx_mock"),
]


async def test__exception_middleware__handler_called(
    incoming_message_factory: Callable[..., IncomingMessage],
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    exc = ValueError("test_error")
    value_error_handler = MagicMock(asyncio.Future())

    user_command = incoming_message_factory(body="/command")

    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        raise exc

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={ValueError: value_error_handler},
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert len(value_error_handler.mock_calls) == 1
    assert value_error_handler.mock_calls[0] == call(user_command, built_bot, exc)


async def test__exception_middleware__without_handler_logs(
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")

    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        raise ValueError("Testing exception middleware")

    built_bot = Bot(collectors=[collector], bot_accounts=[bot_account])

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        with pytest.raises(ValueError) as exc:
            await bot.async_execute_bot_command(user_command)

    # - Assert -
    assert "Testing exception middleware" in str(exc.value)


async def test__exception_middleware__error_in_handler_logs(
    incoming_message_factory: Callable[..., IncomingMessage],
    loguru_caplog: pytest.LogCaptureFixture,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    user_command = incoming_message_factory(body="/command")

    async def exception_handler(
        message: IncomingMessage,
        bot: Bot,
        exc: Exception,
    ) -> None:
        raise ValueError("Nested error")

    collector = HandlerCollector()

    @collector.command("/command", description="My command")
    async def handler(message: IncomingMessage, bot: Bot) -> None:
        raise ValueError("Testing exception middleware")

    built_bot = Bot(
        collectors=[collector],
        bot_accounts=[bot_account],
        exception_handlers={Exception: exception_handler},
    )

    # - Act -
    async with lifespan_wrapper(built_bot) as bot:
        bot.async_execute_bot_command(user_command)

    # - Assert -
    assert "Uncaught exception ValueError in exception handler" in loguru_caplog.text
    assert "Testing exception middleware" in loguru_caplog.text
    assert "Nested error" in loguru_caplog.text
