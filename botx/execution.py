from typing import Any, Callable, Dict, List, Type, cast

from loguru import logger

from .helpers import call_function_as_coroutine
from .models import CommandCallback


async def _handle_exception(
    exceptions_map: Dict[Type[Exception], Callable],
    exc: Exception,
    *args: Any,
    **kwargs: Any,
) -> bool:
    for cls in cast(List[Type[Exception]], type(exc).mro()):
        if cls in exceptions_map:
            exc_catcher = exceptions_map[cls]

            try:
                await call_function_as_coroutine(exc_catcher, exc, *args, **kwargs)
                return True
            except Exception as catcher_exc:
                exceptions_map = exceptions_map.copy()
                exceptions_map.pop(cls)
                catching_basic_exc_res = await _handle_exception(
                    exceptions_map, exc, *args, **kwargs
                )
                catching_catcher_exc_res = await _handle_exception(
                    exceptions_map, catcher_exc, *args, **kwargs
                )
                if catching_basic_exc_res and catching_catcher_exc_res:
                    return True
                logger.exception(
                    f"uncaught exception {catcher_exc !r} during catching {exc !r}"
                )

    return False


async def execute_callback_with_exception_catching(
    exceptions_map: Dict[Type[Exception], Callable], callback: CommandCallback
) -> None:
    try:
        await call_function_as_coroutine(
            callback.callback, *callback.args, **callback.kwargs
        )
    except Exception as exc:
        catcher_res = await _handle_exception(
            exceptions_map, exc, *callback.args, **callback.kwargs
        )
        if not catcher_res:
            logger.exception(f"uncaught exception {exc !r}")
