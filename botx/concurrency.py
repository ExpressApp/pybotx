"""Helpers for execution functions as coroutines."""

import asyncio
import functools
import inspect
from typing import Any, Callable, Coroutine

try:
    import contextvars  # Python 3.7+ only.  # noqa: WPS440, WPS433
except ImportError:  # pragma: no cover
    contextvars = None  # type: ignore  # noqa: WPS440


async def run_in_threadpool(call: Callable, *args: Any, **kwargs: Any) -> Any:
    """Run regular function (not a coroutine) as awaitable coroutine.

    Arguments:
        call: function that should be called as coroutine.
        args: positional arguments for the function.
        kwargs: keyword arguments for the function.

    Returns:
        Result of function call.
    """
    loop = asyncio.get_event_loop()
    if contextvars is not None:  # pragma: no cover
        # Ensure we run in the same context
        child = functools.partial(call, *args, **kwargs)
        context = contextvars.copy_context()
        call = context.run
        args = (child,)
    elif kwargs:  # pragma: no cover
        # loop.run_in_executor doesn't accept 'kwargs', so bind them in here
        call = functools.partial(call, **kwargs)
    return await loop.run_in_executor(None, call, *args)


def is_coroutine_callable(call: Callable) -> bool:
    """Check if object is a coroutine or an object which __call__ method is coroutine.

    Arguments:
        call: callable for checking.

    Returns:
        Result of check.
    """
    if inspect.isfunction(call) or inspect.ismethod(call):
        return asyncio.iscoroutinefunction(call)
    call = getattr(call, "__call__", None)  # noqa: B004
    return asyncio.iscoroutinefunction(call)


def callable_to_coroutine(func: Callable, *args: Any, **kwargs: Any) -> Coroutine:
    """Transform callable to coroutine.

    Arguments:
        func: function that can be sync or async and should be transformed into
            corouine.
        args: positional arguments for this function.
        kwargs: key arguments for this function.

    Returns:
        Coroutine object from passed callable.
    """
    if is_coroutine_callable(func):
        return func(*args, **kwargs)

    return run_in_threadpool(func, *args, **kwargs)
