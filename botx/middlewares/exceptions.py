"""Definition of base middleware class and some default middlewares."""

from typing import Callable, Dict, Optional, Type

from loguru import logger

from botx import concurrency
from botx.models import messages
from botx.typing import Executor
from botx.utils import LogsShapeBuilder


class ExceptionMiddleware:
    """Custom middleware that is default and used to handle registered errors."""

    def __init__(self, executor: Executor) -> None:
        """Init middleware with required params.

        Arguments:
            executor: callable object that accept message and will be executed after
                middleware.
        """
        self.executor = executor
        self._exception_handlers: Dict[Type[Exception], Callable] = {}

    async def __call__(self, message: messages.Message) -> None:
        """Wrap executor for catching exception or log them.

        Arguments:
            message: incoming message that will be passed to executor.
        """
        try:
            await concurrency.callable_to_coroutine(self.executor, message)
        except Exception as exc:
            await self._handle_error_in_handler(exc, message)
        else:
            return

    def add_exception_handler(
        self, exc_class: Type[Exception], handler: Callable
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

    async def _handle_error_in_handler(
        self, exc: Exception, message: messages.Message
    ) -> None:
        """Pass error back to handler if there is one or log error.

        Arguments:
            exc: exception that occurred.
            message: message on which exception occurred.
        """
        handler = self._lookup_handler_for_exception(exc)

        if handler is None:
            logger.bind(
                botx_error=True, payload=LogsShapeBuilder.get_message_shape(message)
            ).exception("uncaught {0} exception {1}", type(exc).__name__, exc)
            return

        await concurrency.callable_to_coroutine(handler, exc, message)
