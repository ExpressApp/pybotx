from typing import Union

from botx.models.message.incoming_message import BotAPIIncomingMessage, IncomingMessage
from botx.models.system_events.added_to_chat import AddedToChatEvent, BotAPIAddedToChat
from botx.models.system_events.chat_created import BotAPIChatCreated, ChatCreatedEvent
from botx.models.system_events.cts_login import BotAPICTSLogin, CTSLoginEvent
from botx.models.system_events.cts_logout import BotAPICTSLogout, CTSLogoutEvent
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
    BotAPICTSLogin,
    BotAPICTSLogout,
]
BotAPICommand = Union[BotAPIIncomingMessage, BotAPISystemEvent]

SystemEvent = Union[
    ChatCreatedEvent,
    AddedToChatEvent,
    DeletedFromChatEvent,
    LeftFromChatEvent,
    CTSLoginEvent,
    CTSLogoutEvent,
]
BotCommand = Union[IncomingMessage, SystemEvent]
