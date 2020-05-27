from typing import Callable, Type

from starlette.middleware.base import RequestResponseEndpoint

from botx.clients.methods.base import BotXMethod


def bind_implementation_to_method(
    method: Type[BotXMethod],
) -> Callable[[RequestResponseEndpoint], RequestResponseEndpoint]:
    def decorator(func: RequestResponseEndpoint) -> RequestResponseEndpoint:
        func.method = method  # type: ignore
        return func

    return decorator
