from dataclasses import dataclass
from typing import List
from uuid import UUID

from botx.models.api_base import VerifiedPayloadBaseModel
from botx.models.enums import BotAPIEntityTypes
from botx.models.message.mentions import BotAPIMentionData, MentionList

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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