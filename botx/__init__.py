"""A little python framework for building bots for Express."""

from loguru import logger

from botx.bots.bots import Bot
from botx.clients.clients.async_client import AsyncClient
from botx.clients.clients.sync_client import Client
from botx.clients.types.message_payload import InternalBotNotificationPayload
from botx.collecting.collectors.collector import Collector
from botx.dependencies.injection_params import Depends
from botx.exceptions import BotXAPIError, DependencyFailure, TokenError, UnknownBotError
from botx.models.attachments import (
    AttachList,
    Attachment,
    Contact,
    Document,
    Image,
    Link,
    Location,
    Video,
    Voice,
)
from botx.models.buttons import BubbleElement, KeyboardElement
from botx.models.credentials import BotXCredentials
from botx.models.entities import (
    ChatMention,
    Entity,
    EntityList,
    Forward,
    Mention,
    Reply,
    UserMention,
)
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
from botx.models.events import ChatCreatedEvent, InternalBotNotificationEvent
from botx.models.files import File
from botx.models.menu import Status
from botx.models.messages.incoming_message import IncomingMessage
from botx.models.messages.message import Message
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.messages.sending.markup import MessageMarkup
from botx.models.messages.sending.message import SendingMessage
from botx.models.messages.sending.options import MessageOptions, NotificationOptions
from botx.models.messages.sending.payload import MessagePayload, UpdatePayload
from botx.models.status import StatusRecipient
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
    "DependencyFailure",
    "UnknownBotError",
    "TokenError",
    # DI
    "Depends",
    # models
    # murkup
    "BubbleElement",
    "KeyboardElement",
    # credentials
    "BotXCredentials",
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
    "InternalBotNotificationEvent",
    # files
    "File",
    # attachments
    "Image",
    "Video",
    "Document",
    "Voice",
    "Location",
    "Contact",
    "Link",
    "Attachment",
    "AttachList",
    # mentions
    "Mention",
    "ChatMention",
    "UserMention",
    # status
    "Status",
    "StatusRecipient",
    # messages
    # handler message
    "Message",
    # incoming
    "IncomingMessage",
    "Entity",
    "EntityList",
    "Forward",
    "Reply",
    # sending
    "SendingCredentials",
    "SendingMessage",
    "MessageMarkup",
    "MessageOptions",
    "NotificationOptions",
    "MessagePayload",
    "UpdatePayload",
    "InternalBotNotificationPayload",
    # testing
    "TestClient",
    "MessageBuilder",
)

logger.disable("botx")
