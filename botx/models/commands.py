from typing import Union

from botx.models.message.incoming_message import BotAPIIncomingMessage, IncomingMessage
from botx.models.system_events.added_to_chat import AddedToChatEvent, BotAPIAddedToChat
from botx.models.system_events.chat_created import BotAPIChatCreated, ChatCreatedEvent
from botx.models.system_events.deleted_from_chat import (
    BotAPIDeletedFromChat,
    DeletedFromChatEvent,
)
from botx.models.system_events.left_from_chat import (
    BotAPILeftFromChat,
    LeftFromChatEvent,
)

BotAPISystemEvent = Union[
    BotAPIChatCreated,
    BotAPIAddedToChat,
    BotAPIDeletedFromChat,
    BotAPILeftFromChat,
]
BotAPICommand = Union[BotAPIIncomingMessage, BotAPISystemEvent]

SystemEvent = Union[
    ChatCreatedEvent,
    AddedToChatEvent,
    DeletedFromChatEvent,
    LeftFromChatEvent,
]
BotCommand = Union[IncomingMessage, SystemEvent]
