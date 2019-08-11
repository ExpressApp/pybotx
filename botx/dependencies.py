import inspect
from typing import TYPE_CHECKING, Any, Callable, Dict

from .helpers import call_function_as_coroutine
from .models import Dependency, Message

if TYPE_CHECKING:  # pragma: no cover
    from .bots import BaseBot


def Depends(dependency: Callable) -> Any:  # noqa: N802
    return Dependency(call=dependency)


async def solve_dependencies(
    message: Message, bot: "BaseBot", dependency: Dependency
) -> Dict[str, Any]:
    from .bots import BaseBot

    sig = inspect.signature(dependency.call)
    dep_params: Dict[str, Any] = {}
    for param in sig.parameters.values():
        if issubclass(param.annotation, Message):
            dep_params[param.name] = message
        elif issubclass(param.annotation, BaseBot):
            dep_params[param.name] = bot
        elif isinstance(param.default, Dependency):
            sub_dep_call = param.default.call
            sub_dep_dependencies = await solve_dependencies(message, bot, param.default)
            dep_params[param.name] = await call_function_as_coroutine(
                sub_dep_call, **sub_dep_dependencies
            )

    return dep_params
