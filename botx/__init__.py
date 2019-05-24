from pydantic import ValidationError

from .bot.dispatcher.command_handler import CommandHandler
from .bot.router import CommandRouter
from .core import BotXException
from .types import (
    CTS,
    BotCredentials,
    BubbleElement,
    ChatTypeEnum,
    CommandUIElement,
    CTSCredentials,
    File,
    KeyboardElement,
    Mention,
    MentionTypeEnum,
    MentionUser,
    MenuCommand,
    Message,
    MessageCommand,
    MessageUser,
    RequestTypeEnum,
    Status,
    StatusEnum,
    StatusResult,
    SyncID,
)

try:
    import aiohttp  # noqa
    from .bot.async_bot import AsyncBot
except ImportError:
    AsyncBot = None  # type: ignore

try:
    import requests  # noqa
    from .bot.sync_bot import SyncBot as Bot
except ImportError:
    Bot = None  # type: ignore


__all__ = (
    "AsyncBot",
    "Bot",
    "CommandHandler",
    "CommandRouter",
    "BotXException",
    "ValidationError",
    "CTS",
    "BotCredentials",
    "BubbleElement",
    "ChatTypeEnum",
    "CommandUIElement",
    "CTSCredentials",
    "File",
    "KeyboardElement",
    "Mention",
    "MentionTypeEnum",
    "MentionUser",
    "MenuCommand",
    "Message",
    "MessageCommand",
    "MessageUser",
    "RequestTypeEnum",
    "Status",
    "StatusEnum",
    "StatusResult",
    "SyncID",
)
