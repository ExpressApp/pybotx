from dataclasses import dataclass
from datetime import datetime
from typing import Union
from uuid import UUID

from botx.bot.models.commands.enums import MentionTypes
from botx.shared_models.chat_types import ChatTypes


@dataclass
class Mention:
    type: MentionTypes
    huid: UUID
    name: str


@dataclass
class Forward:
    chat_id: UUID
    huid: UUID
    type: ChatTypes
    chat_name: str
    sync_id: UUID
    created_at: datetime


@dataclass
class Reply:
    chat_id: UUID
    huid: UUID
    type: ChatTypes
    chat_name: str
    sync_id: UUID
    body: str


Entity = Union[Mention, Forward, Reply]
