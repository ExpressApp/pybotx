"""Decorator for binding custom BotXMethod with implementation."""
from typing import Any, Callable, Type

from botx.clients.methods.base import BotXMethod


def bind_implementation_to_method(method: Type[BotXMethod]) -> Callable[..., Any]:
    """Bind implementation of async route to method.

    Arguments:
        method: method class to bind.

    Returns:
        Decorator that binds method and returns it.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func.method = method  # type: ignore
        return func

    return decorator
