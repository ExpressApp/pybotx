from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase
from pybotx.domain.models.chats import Chat
from pybotx.domain.models.enums import UserKinds


@dataclass(slots=True)
class ChatCreatedMember:
    """ChatCreatedEvent member.

    Attributes:
        is_admin: Is user admin.
        huid: User huid.
        username: Username.
        kind: User type.
    """

    is_admin: bool
    huid: UUID
    username: str | None
    kind: UserKinds


@dataclass(slots=True)
class ChatCreatedEvent(BotCommandBase):
    """Event `system:chat_created`.

    Attributes:
        sync_id: Event sync id.
        chat_id: Created chat id.
        chat_name: Created chat name.
        chat_type: Created chat type.
        host: Created chat cts host.
        creator_id: Creator huid.
        members: List of created chat members.
    """

    chat: Chat
    sync_id: UUID
    chat_name: str
    creator_id: UUID
    members: list[ChatCreatedMember]
