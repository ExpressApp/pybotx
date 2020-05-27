from typing import Any, Callable, Type

from botx.clients.methods.base import BotXMethod


def bind_implementation_to_method(
    method: Type[BotXMethod],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func.method = method  # type: ignore
        return func

    return decorator
