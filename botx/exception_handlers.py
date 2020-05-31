"""Define several handlers for builtin exceptions from this library."""

from typing import Any

from loguru import logger

from botx.models.messages import message as messages


async def dependency_failure_exception_handler(*_: Any) -> None:
    """Just do nothing if there is this error, since it's just a signal for stop.

    Arguments:
        _: default arguments passed to exception handler.
    """


async def no_match_found_exception_handler(
    _: Exception, message: messages.Message,
) -> None:
    """Log that handler was not found.

    Arguments:
        _: raised exception, that is useless, since it is global handler.
        message: message on which processing error was raised.
    """
    logger.info("handler for {0} was not found", message.body)
