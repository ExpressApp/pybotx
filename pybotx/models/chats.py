from dataclasses import dataclass
from datetime import datetime
from datetime import datetime as dt
from typing import List, Optional
from uuid import UUID

from pybotx.models.enums import ChatTypes, IncomingChatTypes, UserKinds


@dataclass
class Chat:
    id: UUID
    type: IncomingChatTypes


@dataclass
class ChatListItem:
    """Chat from list.

    Attributes:
        chat_id: Chat id.
        chat_type: Chat Type.
        name: Chat name.
        description: Chat description.
        members: Chat members.
        created_at: Chat creation datetime.
        updated_at: Last chat update datetime.
        shared_history: Is shared history enabled.
    """

    chat_id: UUID
    chat_type: ChatTypes
    name: str
    description: Optional[str]
    members: List[UUID]
    created_at: datetime
    updated_at: datetime
    shared_history: bool


@dataclass
class ChatInfoMember:
    """Chat member.

    Attributes:
        is_admin: Is user admin.
        huid: User huid.
        kind: User type.
    """

    is_admin: bool
    huid: UUID
    kind: UserKinds


@dataclass
class ChatInfo:
    """Chat information.

    Attributes:
        chat_type: Chat type.
        creator_id: Chat creator id.
        description: Chat description.
        chat_id: Chat id.
        created_at: Chat creation datetime.
        members: Chat members.
        name: Chat name.
        shared_history: Is shared history enabled.
    """

    chat_type: ChatTypes
    creator_id: Optional[UUID]
    description: Optional[str]
    chat_id: UUID
    created_at: dt
    members: List[ChatInfoMember]
    name: str
    shared_history: bool
