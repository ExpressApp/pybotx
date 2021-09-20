from dataclasses import dataclass
from typing import TYPE_CHECKING, Awaitable, Callable, List, TypeVar, Union

from botx.bot.models.commands.commands import BotCommand, SystemEvent
from botx.bot.models.commands.incoming_message import IncomingMessage
from botx.bot.models.status.recipient import StatusRecipient

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440

if TYPE_CHECKING:  # To avoid circular import
    from botx.bot.bot import Bot

TBotCommand = TypeVar("TBotCommand", bound=BotCommand)
HandlerFunc = Callable[[TBotCommand, "Bot"], Awaitable[None]]

IncomingMessageHandlerFunc = HandlerFunc[IncomingMessage]
SystemEventHandlerFunc = HandlerFunc[SystemEvent]

VisibleFunc = Callable[[StatusRecipient, "Bot"], Awaitable[bool]]

Middleware = Callable[
    [IncomingMessage, "Bot", IncomingMessageHandlerFunc],
    Awaitable[None],
]


@dataclass
class BaseIncomingMessageHandler:
    handler_func: IncomingMessageHandlerFunc
    middlewares: List[Middleware]


@dataclass
class HiddenCommandHandler(BaseIncomingMessageHandler):
    # Default should be here, see: https://github.com/python/mypy/issues/6113
    visible: Literal[False] = False


@dataclass
class VisibleCommandHandler(BaseIncomingMessageHandler):
    description: str
    visible: Union[Literal[True], VisibleFunc] = True


@dataclass
class DefaultMessageHandler(BaseIncomingMessageHandler):
    """Just for separate type."""


CommandHandler = Union[HiddenCommandHandler, VisibleCommandHandler]
