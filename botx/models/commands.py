from typing import Union

from botx.models.message.incoming_message import BotAPIIncomingMessage, IncomingMessage
from botx.models.system_events.added_to_chat import AddedToChatEvent, BotAPIAddedToChat
from botx.models.system_events.chat_created import BotAPIChatCreated, ChatCreatedEvent
from botx.models.system_events.deleted_from_chat import (
    BotAPIDeletedFromChat,
    DeletedFromChatEvent,
)

BotAPISystemEvent = Union[BotAPIChatCreated, BotAPIAddedToChat, BotAPIDeletedFromChat]
BotAPICommand = Union[BotAPIIncomingMessage, BotAPISystemEvent]

SystemEvent = Union[ChatCreatedEvent, AddedToChatEvent, DeletedFromChatEvent]
BotCommand = Union[IncomingMessage, SystemEvent]
