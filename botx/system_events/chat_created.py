from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from botx.base import BotXCommandBase
from botx.enums import ChatTypes, UserKinds


@dataclass
class ChatCreatedMember:
    is_admin: bool
    huid: UUID
    username: Optional[str]
    kind: UserKinds


@dataclass
class ChatCreatedEvent(BotXCommandBase):
    sync_id: UUID
    chat_id: UUID
    bot_id: UUID
    host: str
    chat_name: str
    chat_type: ChatTypes
    creator_id: UUID
    members: List[ChatCreatedMember]
