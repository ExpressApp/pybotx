"""A little python framework for building bots for Express."""

from loguru import logger

from botx.bots.bots import Bot
from botx.clients.clients.async_client import AsyncClient
from botx.clients.clients.sync_client import Client
from botx.collecting.collector import Collector
from botx.dependencies.injection_params import Depends
from botx.exceptions import BotXAPIError
from botx.exceptions import DependencyFailure
from botx.exceptions import ServerUnknownError
from botx.models.buttons import BubbleElement
from botx.models.buttons import KeyboardElement
from botx.models.credentials import ExpressServer
from botx.models.credentials import ServerCredentials
from botx.models.enums import ChatTypes
from botx.models.enums import CommandTypes
from botx.models.enums import EntityTypes
from botx.models.enums import Recipients
from botx.models.enums import Statuses
from botx.models.enums import SystemEvents
from botx.models.enums import UserKinds
from botx.models.errors import BotDisabledErrorData
from botx.models.errors import BotDisabledResponse
from botx.models.events import ChatCreatedEvent
from botx.models.files import File
from botx.models.mentions import ChatMention
from botx.models.mentions import Mention
from botx.models.mentions import MentionTypes
from botx.models.mentions import UserMention
from botx.models.menu import Status
from botx.models.messages import Message
from botx.models.messages import SendingMessage
from botx.models.receiving import Entity
from botx.models.receiving import IncomingMessage
from botx.models.sending import MessageMarkup
from botx.models.sending import MessageOptions
from botx.models.sending import MessagePayload
from botx.models.sending import NotificationOptions
from botx.models.sending import SendingCredentials
from botx.models.sending import UpdatePayload
from botx.testing.builder import MessageBuilder

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
