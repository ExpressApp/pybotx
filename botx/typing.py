"""Aliases for complex types from `typing`."""

from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar, Union

from botx.models import messages

if TYPE_CHECKING:  # pragma: no cover
    from botx.bots.bots import Bot  # isort: skip  WPS433, F401

ExceptionT = TypeVar("ExceptionT", bound=Exception)

# Something that can handle new message
AsyncExecutor = Callable[[messages.Message], Awaitable[None]]
SyncExecutor = Callable[[messages.Message], None]
Executor = Union[AsyncExecutor, SyncExecutor]

# Middlware dispatchers
AsyncMiddlewareDispatcher = Callable[[messages.Message, AsyncExecutor], Awaitable[None]]
SyncMiddlewareDispatcher = Callable[[messages.Message, SyncExecutor], None]
MiddlewareDispatcher = Union[AsyncMiddlewareDispatcher, SyncMiddlewareDispatcher]

# Exception handlers
AsyncExceptionHandler = Callable[[ExceptionT, messages.Message], Awaitable[None]]
SyncExceptionHandler = Callable[[ExceptionT, messages.Message], None]
ExceptionHandler = Union[AsyncExceptionHandler, SyncExceptionHandler]

# Startup and shutdown events
AsyncLifespanEvent = Callable[["Bot"], Awaitable[None]]
SyncLifespanEvent = Callable[["Bot"], None]
BotLifespanEvent = Union[AsyncLifespanEvent, SyncLifespanEvent]
