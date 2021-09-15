from dataclasses import dataclass
from typing import TYPE_CHECKING, Awaitable, Callable, TypeVar, Union

from botx.bot.models.commands.commands import BotXCommand
from botx.bot.models.commands.incoming_message import IncomingMessage
from botx.bot.models.status.recipient import StatusRecipient

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440

if TYPE_CHECKING:  # To avoid circular import
    from botx.bot.bot import Bot

TBotXCommand = TypeVar("TBotXCommand", bound=BotXCommand)
HandlerFunc = Callable[[TBotXCommand, "Bot"], Awaitable[None]]

IncomingMessageHandler = HandlerFunc[IncomingMessage]

VisibleFunc = Callable[[StatusRecipient, "Bot"], Awaitable[bool]]


@dataclass
class BaseCommandHandler:
    handler_func: IncomingMessageHandler

    async def __call__(self, incoming_message: IncomingMessage, bot: "Bot") -> None:
        await self.handler_func(incoming_message, bot)


@dataclass
class HiddenCommandHandler(BaseCommandHandler):
    # Default should be here, see: https://github.com/python/mypy/issues/6113
    visible: Literal[False] = False


@dataclass
class VisibleCommandHandler(BaseCommandHandler):
    visible: Union[Literal[True], VisibleFunc]
    description: str


@dataclass
class DefaultHandler(BaseCommandHandler):
    """Just for separate type."""


CommandHandler = Union[HiddenCommandHandler, VisibleCommandHandler]
