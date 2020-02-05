"""Aliases for complex types from `typing`."""

from typing import Any, Awaitable, Callable, Coroutine, TypeVar, Union

from botx.models import messages

ExceptionT = TypeVar("ExceptionT", bound=Exception)

AsyncExecutor = Callable[[messages.Message], Coroutine[Any, Any, None]]
SyncExecutor = Callable[[messages.Message], None]
Executor = Union[AsyncExecutor, SyncExecutor]
MiddlewareDispatcher = Callable[[messages.Message, Executor], Awaitable[None]]
AsyncExceptionHandler = Callable[
    [ExceptionT, messages.Message], Coroutine[Any, Any, None]
]
SyncExceptionHandler = Callable[[ExceptionT, messages.Message], None]
ExceptionHandler = Union[AsyncExceptionHandler, SyncExceptionHandler]
