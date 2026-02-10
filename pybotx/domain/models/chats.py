from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pybotx.domain.models.enums import ChatLinkTypes, ChatTypes, IncomingChatTypes, UserKinds


@dataclass(slots=True)
class Chat:
    id: UUID
    type: IncomingChatTypes


@dataclass(slots=True)
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
    description: str | None
    members: list[UUID]
    created_at: datetime
    updated_at: datetime
    shared_history: bool


@dataclass(slots=True)
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


@dataclass(slots=True)
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
    creator_id: UUID | None
    description: str | None
    chat_id: UUID
    created_at: datetime
    members: list[ChatInfoMember]
    name: str
    shared_history: bool


@dataclass(slots=True)
class ChatLink:
    """Chat invite link."""

    url: str
    link_type: ChatLinkTypes
    access_code: str | None
    link_ttl: int | None
