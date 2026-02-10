from pybotx.domain.models.message.incoming_message import IncomingMessage
from pybotx.domain.models.system_events.added_to_chat import AddedToChatEvent
from pybotx.domain.models.system_events.chat_created import ChatCreatedEvent
from pybotx.domain.models.system_events.chat_deleted_by_user import ChatDeletedByUserEvent
from pybotx.domain.models.system_events.conference_changed import ConferenceChangedEvent
from pybotx.domain.models.system_events.conference_created import ConferenceCreatedEvent
from pybotx.domain.models.system_events.conference_deleted import ConferenceDeletedEvent
from pybotx.domain.models.system_events.cts_login import CTSLoginEvent
from pybotx.domain.models.system_events.cts_logout import CTSLogoutEvent
from pybotx.domain.models.system_events.deleted_from_chat import DeletedFromChatEvent
from pybotx.domain.models.system_events.event_delete import EventDeleted
from pybotx.domain.models.system_events.event_edit import EventEdit
from pybotx.domain.models.system_events.internal_bot_notification import (
    InternalBotNotificationEvent,
)
from pybotx.domain.models.system_events.left_from_chat import LeftFromChatEvent
from pybotx.domain.models.system_events.smartapp_event import SmartAppEvent
from pybotx.domain.models.system_events.user_joined_to_chat import JoinToChatEvent

# Just sorted as below, no real profits
SystemEvent = (
    SmartAppEvent
    | InternalBotNotificationEvent
    | ChatCreatedEvent
    | ChatDeletedByUserEvent
    | AddedToChatEvent
    | DeletedFromChatEvent
    | LeftFromChatEvent
    | CTSLoginEvent
    | CTSLogoutEvent
    | EventDeleted
    | EventEdit
    | JoinToChatEvent
    | ConferenceChangedEvent
    | ConferenceCreatedEvent
    | ConferenceDeletedEvent
)
BotCommand = IncomingMessage | SystemEvent

__all__: list[str] = [
    "IncomingMessage",
    "SystemEvent",
    "BotCommand",
]
