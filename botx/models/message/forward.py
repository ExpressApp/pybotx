from dataclasses import dataclass
from uuid import UUID

from botx.models.api_base import VerifiedPayloadBaseModel
from botx.models.enums import BotAPIEntityTypes

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class Forward:
    chat_id: UUID
    author_id: UUID
    sync_id: UUID


class BotAPIForwardData(VerifiedPayloadBaseModel):
    group_chat_id: UUID
    sender_huid: UUID
    source_sync_id: UUID


class BotAPIForward(VerifiedPayloadBaseModel):
    type: Literal[BotAPIEntityTypes.FORWARD]
    data: BotAPIForwardData
