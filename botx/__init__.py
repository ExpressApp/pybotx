"""A little python framework for building bots for Express."""

from loguru import logger

from botx.bots import Bot
from botx.clients import AsyncClient, Client
from botx.collecting import Collector
from botx.exceptions import BotXAPIError, DependencyFailure, ServerUnknownError
from botx.models.buttons import BubbleElement, KeyboardElement
from botx.models.credentials import ExpressServer, ServerCredentials
from botx.models.enums import (
    ChatTypes,
    CommandTypes,
    Recipients,
    Statuses,
    SystemEvents,
    UserKinds,
)
from botx.models.errors import BotDisabledErrorData, BotDisabledResponse
from botx.models.events import ChatCreatedEvent
from botx.models.files import File
from botx.models.mentions import ChatMention, Mention, MentionTypes, UserMention
from botx.models.menu import Status
from botx.models.messages import Message, SendingMessage
from botx.models.receiving import IncomingMessage
from botx.models.sending import (
    MessageMarkup,
    MessageOptions,
    MessagePayload,
    NotificationOptions,
    SendingCredentials,
    UpdatePayload,
)
from botx.params import Depends

__all__ = (
    "Bot",
    "AsyncClient",
    "Client",
    "Collector",
    "BotXAPIError",
    "ServerUnknownError",
    "DependencyFailure",
    "Depends",
    "BubbleElement",
    "KeyboardElement",
    "ExpressServer",
    "ServerCredentials",
    "Statuses",
    "Recipients",
    "UserKinds",
    "ChatTypes",
    "CommandTypes",
    "SystemEvents",
    "BotDisabledErrorData",
    "BotDisabledResponse",
    "ChatCreatedEvent",
    "File",
    "Mention",
    "ChatMention",
    "UserMention",
    "MentionTypes",
    "Status",
    "Message",
    "SendingMessage",
    "IncomingMessage",
    "MessageMarkup",
    "MessageOptions",
    "MessagePayload",
    "NotificationOptions",
    "UpdatePayload",
    "SendingCredentials",
)

logger.disable("botx")
