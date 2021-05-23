"""Exception mixin for bot."""

from typing import Callable, Type

from botx import typing
from botx.middlewares.exceptions import ExceptionMiddleware

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # noqa: WPS433, WPS440, F401


class ExceptionHandlersMixin:
    """Mixin that defines functions for exception handlers registration."""

    exception_middleware: ExceptionMiddleware

    def add_exception_handler(
        self,
        exc_class: Type[Exception],
        handler: typing.ExceptionHandler,
    ) -> None:
        """Register new handler for exception.

        Arguments:
            exc_class: exception type that should be handled.
            handler: handler for exception.
        """
        self.exception_middleware.add_exception_handler(exc_class, handler)

    def exception_handler(self, exc_class: Type[Exception]) -> Callable:
        """Register callable as handler for exception.

        Arguments:
            exc_class: exception type that should be handled.

        Returns:
            Decorator that will register exception and return passed function.
        """

        def decorator(handler: typing.ExceptionHandler) -> Callable:
            self.add_exception_handler(exc_class, handler)
            return handler

        return decorator
