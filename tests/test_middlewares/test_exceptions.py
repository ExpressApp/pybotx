import pytest
from _pytest.logging import LogCaptureFixture

from botx import Bot, IncomingMessage, Message, TestClient


@pytest.mark.asyncio
async def test_handling_exception_through_custom_catcher(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    bot.collector.default_message_handler = None

    exc_value = None
    exc_message = None

    exc_for_raising = Exception("exception from handler")

    @bot.exception_handler(Exception)
    def exception_handler(exc: Exception, msg: Message) -> None:
        nonlocal exc_value, exc_message
        exc_value = exc
        exc_message = msg

    @bot.default
    def handler_that_raises_error() -> None:
        raise exc_for_raising

    await client.send_command(incoming_message)

    assert exc_value == exc_for_raising
    assert exc_message.incoming_message == incoming_message


@pytest.mark.asyncio
async def test_handling_exception_through_nearest_custom_catcher(
    bot: Bot, incoming_message: IncomingMessage, client: TestClient
) -> None:
    bot.collector.default_message_handler = None

    exc_value = None

    exc_for_raising = UnicodeError("exception from handler")

    @bot.exception_handler(Exception)
    def exception_handler(_: Exception, __: Message) -> None:
        ...  # pragma: no cover

    @bot.exception_handler(ValueError)
    def valuer_error_handler(exc: Exception, _: Message) -> None:
        nonlocal exc_value
        exc_value = exc

    @bot.default
    def handler_that_raises_error() -> None:
        raise exc_for_raising

    await client.send_command(incoming_message)

    assert exc_value == exc_for_raising


@pytest.mark.asyncio
async def test_logging_exception_if_was_not_found(
    bot: Bot,
    incoming_message: IncomingMessage,
    loguru_caplog: LogCaptureFixture,
    client: TestClient,
) -> None:
    bot.collector.default_message_handler = None

    @bot.default
    def handler_that_raises_error() -> None:
        raise ValueError

    await client.send_command(incoming_message)

    assert "uncaught ValueError exception" in loguru_caplog.text
