from dataclasses import dataclass
from typing import List, Literal
from uuid import UUID

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.enums import BotAPIEntityTypes
from pybotx.models.message.mentions import BotAPIMentionData, MentionList


@dataclass
class Reply:
    author_id: UUID
    sync_id: UUID
    body: str
    mentions: MentionList


class BotAPIReplyData(VerifiedPayloadBaseModel):
    source_sync_id: UUID
    sender: UUID
    body: str
    mentions: List[BotAPIMentionData]
    # Ignoring attachments cause they don't have content


class BotAPIReply(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.REPLY]
    data: BotAPIReplyData
