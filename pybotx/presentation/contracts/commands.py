from pybotx.presentation.contracts.message.incoming_message import BotAPIIncomingMessage
from pybotx.presentation.contracts.system_events.added_to_chat import BotAPIAddedToChat
from pybotx.presentation.contracts.system_events.chat_created import BotAPIChatCreated
from pybotx.presentation.contracts.system_events.chat_deleted_by_user import (
    BotAPIChatDeletedByUser,
)
from pybotx.presentation.contracts.system_events.conference_changed import (
    BotAPIConferenceChanged,
)
from pybotx.presentation.contracts.system_events.conference_created import (
    BotAPIConferenceCreated,
)
from pybotx.presentation.contracts.system_events.conference_deleted import (
    BotAPIConferenceDeleted,
)
from pybotx.presentation.contracts.system_events.cts_login import BotAPICTSLogin
from pybotx.presentation.contracts.system_events.cts_logout import BotAPICTSLogout
from pybotx.presentation.contracts.system_events.deleted_from_chat import (
    BotAPIDeletedFromChat,
)
from pybotx.presentation.contracts.system_events.event_delete import BotAPIEventDeleted
from pybotx.presentation.contracts.system_events.event_edit import BotAPIEventEdit
from pybotx.presentation.contracts.system_events.internal_bot_notification import (
    BotAPIInternalBotNotification,
)
from pybotx.presentation.contracts.system_events.left_from_chat import BotAPILeftFromChat
from pybotx.presentation.contracts.system_events.smartapp_event import (
    BotAPISmartAppEvent,
)
from pybotx.presentation.contracts.system_events.user_joined_to_chat import (
    BotAPIJoinToChat,
)

# Sorted by frequency of occurrence to speedup validation
BotAPISystemEvent = (
    BotAPISmartAppEvent
    | BotAPIInternalBotNotification
    | BotAPIChatCreated
    | BotAPIChatDeletedByUser
    | BotAPIAddedToChat
    | BotAPIDeletedFromChat
    | BotAPILeftFromChat
    | BotAPICTSLogin
    | BotAPICTSLogout
    | BotAPIEventDeleted
    | BotAPIEventEdit
    | BotAPIJoinToChat
    | BotAPIConferenceChanged
    | BotAPIConferenceCreated
    | BotAPIConferenceDeleted
)
BotAPICommand = BotAPIIncomingMessage | BotAPISystemEvent

__all__ = [
    "BotAPIIncomingMessage",
    "BotAPISystemEvent",
    "BotAPICommand",
]
