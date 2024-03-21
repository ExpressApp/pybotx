from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.enums import BotAPIEntityTypes


@dataclass
class Forward:
    chat_id: UUID
    author_id: UUID
    sync_id: UUID
    chat_name: str
    inserted_at: datetime


class BotAPIForwardData(VerifiedPayloadBaseModel):
    group_chat_id: UUID
    sender_huid: UUID
    source_sync_id: UUID
    source_chat_name: str
    source_inserted_at: datetime


class BotAPIForward(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.FORWARD]
    data: BotAPIForwardData
