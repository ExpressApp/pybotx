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
    MentionTypes,
    Statuses,
    SystemEvents,
    UserKinds,
)
from botx.models.errors import BotDisabledErrorData, BotDisabledResponse
from botx.models.events import ChatCreatedEvent
from botx.models.files import File
from botx.models.forwards import Forward
from botx.models.mentions import ChatMention, Mention, UserMention
from botx.models.menu import Status
from botx.models.messages.incoming_message import Entity, IncomingMessage
from botx.models.messages.message import Message
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.messages.sending.markup import MessageMarkup
from botx.models.messages.sending.message import SendingMessage
from botx.models.messages.sending.options import MessageOptions, NotificationOptions
from botx.models.messages.sending.payload import MessagePayload, UpdatePayload
from botx.testing.building.builder import MessageBuilder

try:
    from botx.testing.testing_client.client import TestClient  # noqa: WPS433
except ImportError:
    TestClient = None  # type: ignore  # noqa: WPS440

__all__ = (
    # bots
    "Bot",
    # collecting
    "Collector",
    # clients
    "AsyncClient",
    "Client",
    # exceptions
    "BotXAPIError",
    "ServerUnknownError",
    "DependencyFailure",
    # DI
    "Depends",
    # models
    # murkup
    "BubbleElement",
    "KeyboardElement",
    # credentials
    "ExpressServer",
    "ServerCredentials",
    # enums
    "Statuses",
    "UserKinds",
    "ChatTypes",
    "CommandTypes",
    "SystemEvents",
    "EntityTypes",
    "MentionTypes",
    # errors
    "BotDisabledErrorData",
    "BotDisabledResponse",
    # events
    "ChatCreatedEvent",
    # files
    "File",
    # mentions
    "Mention",
    "ChatMention",
    "UserMention",
    # status
    "Status",
    # messages
    # handler message
    "Message",
    # incoming
    "IncomingMessage",
    "Entity",
    "Forward",
    # sending
    "SendingCredentials",
    "SendingMessage",
    "MessageMarkup",
    "MessageOptions",
    "NotificationOptions",
    "MessagePayload",
    "UpdatePayload",
    # testing
    "TestClient",
    "MessageBuilder",
)

logger.disable("botx")
