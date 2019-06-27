from typing import Optional
from uuid import UUID

from .base import BotXType
from .enums import MentionTypeEnum


class MentionUser(BotXType):
    user_huid: UUID
    name: Optional[str] = None


class Mention(BotXType):
    mention_type: MentionTypeEnum = MentionTypeEnum.user
    mention_data: MentionUser
