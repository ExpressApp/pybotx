from typing import Callable

from botx.clients.methods.base import BotXMethod


def bind_implementation_to_method(method: BotXMethod) -> Callable:
    def decorator(func: Callable):
        func.method = method
        return func

    return decorator
