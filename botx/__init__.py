"""A little python framework for building bots for Express."""

from loguru import logger

from botx.bots.bots import Bot
from botx.clients.clients.async_client import AsyncClient
from botx.clients.clients.sync_client import Client
from botx.collecting.collectors.collector import Collector
from botx.dependencies.injection_params import Depends
from botx.exceptions import BotXAPIError, DependencyFailure, ServerUnknownError
from botx.models.buttons import BubbleElement, KeyboardElement
from botx.models.credentials import ExpressServer, ServerCredentials
from botx.models.enums import (
    ChatTypes,
    CommandTypes,
    EntityTypes,
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
from botx.models.receiving import Entity, IncomingMessage
from botx.models.sending import (
    MessageMarkup,
    MessageOptions,
    MessagePayload,
    NotificationOptions,
    SendingCredentials,
    UpdatePayload,
)
from botx.testing.building.builder import MessageBuilder

try:
    from botx.testing.client import TestClient
except ImportError:
    TestClient = None

__all__ = (
    "Bot",
    "Collector",
    "AsyncClient",
    "Client",
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
    "Entity",
    "EntityTypes",
    "TestClient",
    "MessageBuilder",
)

logger.disable("botx")
