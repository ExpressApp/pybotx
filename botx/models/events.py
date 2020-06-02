"""Definition of different schemas for system events."""

from types import MappingProxyType
from typing import List
from uuid import UUID

from pydantic import BaseModel

from botx.models.enums import ChatTypes, SystemEvents, UserKinds


class UserInChatCreated(BaseModel):
    """User that can be included in data in `system:chat_created` event."""

    #: user HUID.
    huid: UUID

    #: type of user.
    user_kind: UserKinds

    #: user username.
    name: str

    #: is user administrator in chat.
    admin: bool


class ChatCreatedEvent(BaseModel):
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


class AddedToChatEvent(BaseModel):
    """Shape for `system:added_to_chat` event data."""

    #: members added to chat.
    added_members: List[UUID]


# dict for validating shape for different events
EVENTS_SHAPE_MAP = MappingProxyType({SystemEvents.chat_created: ChatCreatedEvent,
                                     SystemEvents.added_to_chat: AddedToChatEvent})
