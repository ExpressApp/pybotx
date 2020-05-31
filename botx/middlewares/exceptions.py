"""Definition of base middleware class and some default middlewares."""

from typing import Callable, Dict, Optional, Type

from loguru import logger

from botx import concurrency
from botx.middlewares.base import BaseMiddleware
from botx.models import files
from botx.models.messages.message import Message
from botx.typing import AsyncExecutor, Executor


class ExceptionMiddleware(BaseMiddleware):
    """Custom middleware that is default and used to handle registered errors."""

    def __init__(self, executor: Executor) -> None:
        """Init middleware with required query_params.

        Arguments:
            executor: callable object that accept message and will be executed after
                middleware.
        """
        super().__init__(executor)
        self._exception_handlers: Dict[Type[Exception], Callable] = {}

    async def dispatch(self, message: Message, call_next: AsyncExecutor) -> None:
        """Wrap executor for catching exception or log them.

        Arguments:
            message: incoming message that will be passed to executor.
            call_next: next executor that should be called after this.
        """
        try:
            await call_next(message)
        except Exception as exc:
            await self._handle_error_in_handler(exc, message)

    def add_exception_handler(
        self, exc_class: Type[Exception], handler: Callable,
    ) -> None:
        """Register handler for specific exception in middleware.

        Arguments:
            exc_class: exception class that should be handled by middleware.
            handler: handler for exception.
        """
        self._exception_handlers[exc_class] = handler

    def _lookup_handler_for_exception(self, exc: Exception) -> Optional[Callable]:
        """Find handler for exception.

        Arguments:
            exc: catched exception for which handler should be found.

        Returns:
            Found handler or None.
        """
        for exc_cls in type(exc).mro():
            handler = self._exception_handlers.get(exc_cls)
            if handler:
                return handler

        return None

    async def _handle_error_in_handler(self, exc: Exception, message: Message) -> None:
        """Pass error back to handler if there is one or log error.

        Arguments:
            exc: exception that occurred.
            message: message on which exception occurred.
        """
        handler = self._lookup_handler_for_exception(exc)

        if handler is None:
            logger.bind(
                botx_error=True,
                payload=message.incoming_message.copy(
                    update={
                        "body": _convert_text_to_logs_format(message.body),
                        "file": _convert_file_to_logs_format(message.file),
                    },
                ).dict(),
            ).exception("uncaught {0} exception {1}", type(exc).__name__, exc)
            return

        await concurrency.callable_to_coroutine(handler, exc, message)


def _convert_text_to_logs_format(text: str) -> str:
    """Convert text into format that is suitable for logs.

    Arguments:
        text: text that should be formatted.

    Returns:
        Shape for logging in loguru.
    """
    max_log_text_length = 50
    start_text_index = 15
    end_text_index = 5

    return (
        "...".join((text[:start_text_index], text[-end_text_index:]))
        if len(text) > max_log_text_length
        else text
    )


def _convert_file_to_logs_format(file: Optional[files.File]) -> Optional[dict]:
    """Convert file to a new file that will be showed in logs.

    Arguments:
        file: file that should be converted.

    Returns:
        New file or nothing.
    """
    return file.copy(update={"data": "[file content]"}).dict() if file else None
