from datetime import datetime
from typing import Literal
from uuid import UUID

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.enums import APIChatTypes, BotAPIEntityTypes


class BotAPIForwardData(VerifiedPayloadBaseModel):
    group_chat_id: UUID
    sender_huid: UUID
    source_sync_id: UUID
    source_chat_name: str
    forward_type: APIChatTypes
    source_inserted_at: datetime


class BotAPIForward(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.FORWARD]
    data: BotAPIForwardData
