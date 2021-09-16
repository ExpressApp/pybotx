from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from botx.bot.models.commands.base import BotCommandBase
from botx.bot.models.commands.enums import ChatTypes, UserKinds


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
    bot_id: UUID
    host: str
    chat_name: str
    chat_type: ChatTypes
    creator_id: UUID
    members: List[ChatCreatedMember]
