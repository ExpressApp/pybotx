from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from botx.bot.models.commands.base import BotCommandBase
from botx.bot.models.commands.enums import UserKinds
from botx.shared_models.domain.enums import ChatTypes


@dataclass
class ChatCreatedMember:
    is_admin: bool
    huid: UUID
    username: Optional[str]
    kind: UserKinds


@dataclass
class ChatCreatedEvent(BotCommandBase):
    sync_id: UUID
    chat_id: UUID
    chat_name: str
    chat_type: ChatTypes
    host: str
    creator_id: UUID
    members: List[ChatCreatedMember]
