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
from botx.models.system_events.internal_bot_notification import (
    BotAPIInternalBotNotification,
    InternalBotNotificationEvent,
)
from botx.models.system_events.left_from_chat import (
    BotAPILeftFromChat,
    LeftFromChatEvent,
)
from botx.models.system_events.smartapp_event import BotAPISmartAppEvent, SmartAppEvent

BotAPISystemEvent = Union[
    BotAPIChatCreated,
    BotAPIAddedToChat,
    BotAPIDeletedFromChat,
    BotAPILeftFromChat,
    BotAPICTSLogin,
    BotAPICTSLogout,
    BotAPIInternalBotNotification,
    BotAPISmartAppEvent,
]
BotAPICommand = Union[BotAPIIncomingMessage, BotAPISystemEvent]

SystemEvent = Union[
    ChatCreatedEvent,
    AddedToChatEvent,
    DeletedFromChatEvent,
    LeftFromChatEvent,
    CTSLoginEvent,
    CTSLogoutEvent,
    InternalBotNotificationEvent,
    SmartAppEvent,
]
BotCommand = Union[IncomingMessage, SystemEvent]
