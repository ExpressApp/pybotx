"""Helpers for execution functions as coroutines."""

import asyncio
import contextvars
import functools
import inspect
from typing import Any, Callable, Coroutine


def is_awaitable_object(call: Callable) -> bool:
    """Check if object is an awaitable or an object which __call__ method is awaitable.

    Arguments:
        call: callable for checking.

    Returns:
        Result of check.
    """
    if is_awaitable(call):
        return True
    call = getattr(call, "__call__", None)  # noqa: B004
    return asyncio.iscoroutinefunction(call)


def is_awaitable(call: Callable) -> bool:
    """Check if function returns awaitable object.

    Arguments:
        call: function that should be checked.

    Returns:
        Result of check.
    """
    if inspect.isfunction(call) or inspect.ismethod(call):
        return asyncio.iscoroutinefunction(call)
    return False


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
    child = functools.partial(call, *args, **kwargs)
    context = contextvars.copy_context()
    call = context.run
    args = (child,)
    return await loop.run_in_executor(None, call, *args)


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
    if is_awaitable_object(func):
        return func(*args, **kwargs)

    return run_in_threadpool(func, *args, **kwargs)


def run_in_blocking_loop(call: Callable, *args: Any, **kwargs: Any) -> Any:
    """Run coroutine with loop blocking.

    Arguments:
        call: function that should be called in loop until complete.
        args: function arguments.
        kwargs: function key arguments.

    Returns:
        Result of function call.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    return loop.run_until_complete(callable_to_coroutine(call, *args, **kwargs))


def async_to_sync(func: Callable) -> Callable:
    """Convert asynchronous function to blocking.

    Arguments:
        func: function that should be converted.

    Returns:
        Converted function.
    """
    return functools.partial(run_in_blocking_loop, func)
