from typing import Literal
from uuid import UUID

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.enums import BotAPIEntityTypes
from pybotx.presentation.contracts.message.mentions import BotAPIMentionData


class BotAPIReplyData(VerifiedPayloadBaseModel):
    source_sync_id: UUID
    sender: UUID
    body: str
    mentions: list[BotAPIMentionData]
    # Ignoring attachments cause they don't have content


class BotAPIReply(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.REPLY]
    data: BotAPIReplyData
