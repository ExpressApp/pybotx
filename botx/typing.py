"""Aliases for complex types from `typing`."""

from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar, Union

from botx.models.messages import message

if TYPE_CHECKING:
    from botx.bots.bots import Bot  # noqa: WPS433

try:
    from typing import Literal  # noqa: WPS433
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS433, WPS440, F401

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
AsyncLifespanEvent = Callable[["Bot"], Awaitable[None]]
SyncLifespanEvent = Callable[["Bot"], None]
BotLifespanEvent = Union[AsyncLifespanEvent, SyncLifespanEvent]
