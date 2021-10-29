from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from botx.bot.models.commands.base import BotCommandBase
from botx.bot.models.commands.enums import UserKinds
from botx.shared_models.chat_types import ChatTypes


@dataclass
class ChatCreatedMember:
    """ChatCreatedEvent member.

    Attributes:
        is_admin: Is user admin.
        huid: User huid.
        username: User name.
        kind: User type. TODO: link to UserKinds
    """

    is_admin: bool
    huid: UUID
    username: Optional[str]
    kind: UserKinds


@dataclass
class ChatCreatedEvent(BotCommandBase):
    """Event `system:chat_created`.

    Attributes:
        sync_id: Event sync id.
        chat_id: Created chat id.
        chat_name: Created chat name.
        chat_type: Created chat type.
        host: Created chat cts host.
        creator_id: Creator huid.
        members: List of [members]\
[botx.bot.models.commands.system_events.chat_created.ChatCreatedMember].
    """

    sync_id: UUID
    chat_id: UUID
    chat_name: str
    chat_type: ChatTypes
    host: str
    creator_id: UUID
    members: List[ChatCreatedMember]
