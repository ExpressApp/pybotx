"""Aliases for complex types from `typing`."""

from typing import Awaitable, Callable, TypeVar, Union

from botx.bots import bots
from botx.models.messages import message

try:
    from typing import Protocol, Literal  # noqa: WPS433
except ImportError:
    from typing_extensions import (  # type: ignore  # noqa: WPS433, WPS440, F401
        Protocol,
        Literal,
    )


ExceptionT = TypeVar("ExceptionT", bound=Exception)

# Something that can handle new message
AsyncExecutor = Callable[[message.Message], Awaitable[None]]
SyncExecutor = Callable[[message.Message], None]
Executor = Union[AsyncExecutor, SyncExecutor]

# Middlware dispatchers
AsyncMiddlewareDispatcher = Callable[[message.Message, AsyncExecutor], Awaitable[None]]
SyncMiddlewareDispatcher = Callable[[message.Message, SyncExecutor], None]
MiddlewareDispatcher = Union[AsyncMiddlewareDispatcher, SyncMiddlewareDispatcher]

# Exception handlers
AsyncExceptionHandler = Callable[[ExceptionT, message.Message], Awaitable[None]]
SyncExceptionHandler = Callable[[ExceptionT, message.Message], None]
ExceptionHandler = Union[AsyncExceptionHandler, SyncExceptionHandler]

# Startup and shutdown events
AsyncLifespanEvent = Callable[["bots.Bot"], Awaitable[None]]
SyncLifespanEvent = Callable[["bots.Bot"], None]
BotLifespanEvent = Union[AsyncLifespanEvent, SyncLifespanEvent]
