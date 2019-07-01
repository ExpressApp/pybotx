from typing import List
from uuid import UUID

from .base import BotXType
from .enums import ChatTypeEnum, UserKindEnum


class UserInChatCreated(BotXType):
    huid: UUID
    user_kind: UserKindEnum
    name: str
    admin: bool


class ChatCreatedData(BotXType):
    group_chat_id: UUID
    chat_type: ChatTypeEnum
    name: str
    creator: UUID
    members: List[UserInChatCreated]
