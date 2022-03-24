from typing import Union

from pybotx.models.message.incoming_message import (
    BotAPIIncomingMessage,
    IncomingMessage,
)
from pybotx.models.system_events.added_to_chat import (
    AddedToChatEvent,
    BotAPIAddedToChat,
)
from pybotx.models.system_events.chat_created import BotAPIChatCreated, ChatCreatedEvent
from pybotx.models.system_events.cts_login import BotAPICTSLogin, CTSLoginEvent
from pybotx.models.system_events.cts_logout import BotAPICTSLogout, CTSLogoutEvent
from pybotx.models.system_events.deleted_from_chat import (
    BotAPIDeletedFromChat,
    DeletedFromChatEvent,
)
from pybotx.models.system_events.internal_bot_notification import (
    BotAPIInternalBotNotification,
    InternalBotNotificationEvent,
)
from pybotx.models.system_events.left_from_chat import (
    BotAPILeftFromChat,
    LeftFromChatEvent,
)
from pybotx.models.system_events.smartapp_event import (
    BotAPISmartAppEvent,
    SmartAppEvent,
)

# Sorted by frequency of occurrence to speedup validation
BotAPISystemEvent = Union[
    BotAPISmartAppEvent,
    BotAPIInternalBotNotification,
    BotAPIChatCreated,
    BotAPIAddedToChat,
    BotAPIDeletedFromChat,
    BotAPILeftFromChat,
    BotAPICTSLogin,
    BotAPICTSLogout,
]
BotAPICommand = Union[BotAPIIncomingMessage, BotAPISystemEvent]

# Just sorted as above, no real profits
SystemEvent = Union[
    SmartAppEvent,
    InternalBotNotificationEvent,
    ChatCreatedEvent,
    AddedToChatEvent,
    DeletedFromChatEvent,
    LeftFromChatEvent,
    CTSLoginEvent,
    CTSLogoutEvent,
]
BotCommand = Union[IncomingMessage, SystemEvent]
