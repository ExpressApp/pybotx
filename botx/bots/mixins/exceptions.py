"""Exception mixin for bot."""

from typing import Callable, Type

from botx import typing
from botx.middlewares.exceptions import ExceptionMiddleware
from botx.typing import Protocol


class ExceptionMiddlewareOwnerProtocol(Protocol):
    """Protocol for owner of core exception middleware."""

    @property
    def exception_middleware(self) -> ExceptionMiddleware:
        """Exception middleware."""


class ExceptionHandlersMixin:
    """Mixin that defines functions for exception handlers registration."""

    def add_exception_handler(
        self: ExceptionMiddlewareOwnerProtocol,
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
