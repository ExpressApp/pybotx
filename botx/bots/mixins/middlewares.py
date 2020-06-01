"""Implementation for bot classes."""

from typing import Any, Callable, Type

from botx import typing
from botx.middlewares.base import BaseMiddleware
from botx.middlewares.exceptions import ExceptionMiddleware


class MiddlewareMixin:
    """Middleware mixin for bot."""

    exception_middleware: ExceptionMiddleware

    def add_middleware(
        self, middleware_class: Type[BaseMiddleware], **kwargs: Any,
    ) -> None:
        """Register new middleware for execution before handler.

        Arguments:
            middleware_class: middleware that should be registered.
            kwargs: arguments that are required for middleware initialization.
        """
        self.exception_middleware.executor = middleware_class(
            self.exception_middleware.executor, **kwargs,
        )

    def middleware(self, handler: typing.Executor) -> Callable:
        """Register callable as middleware for request.

        Arguments:
            handler: handler for middleware logic.

        Returns:
            Passed `handler` callable.
        """
        self.add_middleware(BaseMiddleware, dispatch=handler)
        return handler
