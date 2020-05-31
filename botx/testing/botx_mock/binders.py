"""Decorator for binding custom BotXMethod with implementation."""
from typing import Callable, Type

from starlette.middleware.base import RequestResponseEndpoint

from botx.clients.methods.base import BotXMethod


def bind_implementation_to_method(
    method: Type[BotXMethod],
) -> Callable[[RequestResponseEndpoint], RequestResponseEndpoint]:
    """Bind implementation of async route to method.

    Arguments:
        method: method class to bind.

    Returns:
        Decorator that binds method and returns it.
    """

    def decorator(func: RequestResponseEndpoint) -> RequestResponseEndpoint:
        func.method = method  # type: ignore
        return func

    return decorator
