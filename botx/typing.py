"""Aliases for complex types from `typing`."""

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Coroutine, TypeVar, Union

from botx.models import messages

if TYPE_CHECKING:  # pragma: no cover
    from botx.bots import Bot  # isort: skip  # noqa: WPS433, F401

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

AsyncLifespanEvent = Callable[["Bot"], Awaitable[None]]
SyncLifespanEvent = Callable[["Bot"], None]
BotLifespanEvent = Union[AsyncLifespanEvent, SyncLifespanEvent]
