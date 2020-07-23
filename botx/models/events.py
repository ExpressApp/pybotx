"""Definition of different schemas for system events."""

from types import MappingProxyType
from typing import List
from uuid import UUID

from pydantic import BaseModel

from botx.models.enums import ChatTypes, SystemEvents, UserKinds


class UserInChatCreated(BaseModel):
    """User that can be included in data in `system:chat_created` event."""

    huid: UUID
    """user huid."""
    user_kind: UserKinds
    """type of user."""
    name: str
    """user username."""
    admin: bool
    """is user administrator in chat."""


class ChatCreatedEvent(BaseModel):
    """Shape for `system:chat_created` event data."""

    group_chat_id: UUID
    """chat id from which event received."""
    chat_type: ChatTypes
    """type of chat."""
    name: str
    """chat name."""
    creator: UUID
    """`huid` of user that created chat."""
    members: List[UserInChatCreated]
    """list of users that are members of chat."""


# dict for validating shape for different events
EVENTS_SHAPE_MAP = MappingProxyType({SystemEvents.chat_created: ChatCreatedEvent})
