"""Definition of different schemas for system events."""

from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Type
from uuid import UUID

from botx.clients.types.message_payload import InternalBotNotificationPayload
from botx.models.base import BotXBaseModel
from botx.models.enums import ChatTypes, SystemEvents
from botx.models.users import UserInChatCreated


class ChatCreatedEvent(BotXBaseModel):
    """Shape for `system:chat_created` event data."""

    #: chat id from which event received.
    group_chat_id: UUID

    #: type of chat.
    chat_type: ChatTypes

    #: chat name.
    name: str

    #: HUID of user that created chat.
    creator: UUID

    #: list of users that are members of chat.
    members: List[UserInChatCreated]


class AddedToChatEvent(BotXBaseModel):
    """Shape for `system:added_to_chat` event data."""

    #: members added to chat.
    added_members: List[UUID]


class DeletedFromChatEvent(BotXBaseModel):
    """Shape for `system:deleted_from_chat` event data."""

    #: members deleted from chat
    deleted_members: List[UUID]


class LeftFromChatEvent(BotXBaseModel):
    """Shape for `system:left_from_chat` event data."""

    #: left chat members
    left_members: List[UUID]


class InternalBotNotificationEvent(BotXBaseModel):
    """Shape for `system:internal_bot_notification` event data."""

    #: notification data
    data: InternalBotNotificationPayload  # noqa: WPS110

    #: user-defined extra options
    opts: Dict[str, Any]


class CTSLoginEvent(BotXBaseModel):
    """Shape for `system:cts_login` event data."""

    #: huid of user which logged into CTS.
    user_huid: UUID

    #: CTS id.
    cts_id: UUID


class CTSLogoutEvent(BotXBaseModel):
    """Shape for `system:cts_logout` event data."""

    #: huid of user which logged out from CTS.
    user_huid: UUID

    #: CTS id.
    cts_id: UUID


class SmartAppEvent(BotXBaseModel):
    """Shape for `system:smartapp_event` event data."""

    #: unique request id
    ref: Optional[UUID] = None

    #: smartapp id
    smartapp_id: UUID

    #: event data
    data: Dict[str, Any]  # noqa: WPS110

    #: event options
    opts: Dict[str, Any] = {}

    #: version of protocol smartapp <-> bot
    smartapp_api_version: int


# dict for validating shape for different events
EVENTS_SHAPE_MAP: Mapping[SystemEvents, Type[BotXBaseModel]] = MappingProxyType(
    {
        SystemEvents.chat_created: ChatCreatedEvent,
        SystemEvents.added_to_chat: AddedToChatEvent,
        SystemEvents.deleted_from_chat: DeletedFromChatEvent,
        SystemEvents.left_from_chat: LeftFromChatEvent,
        SystemEvents.internal_bot_notification: InternalBotNotificationEvent,
        SystemEvents.cts_login: CTSLoginEvent,
        SystemEvents.cts_logout: CTSLogoutEvent,
        SystemEvents.smartapp_event: SmartAppEvent,
    },
)
