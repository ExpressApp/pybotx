from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import Field

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.base_command import (
    BaseBotAPIContext,
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
    BotCommandBase,
)
from pybotx.models.bot_account import BotAccount
from pybotx.models.enums import BotAPISystemEventTypes


@dataclass
class EventDeleted(BotCommandBase):
    """Event `system:event_deleted`.

    Attributes:
        deleted_at: Delete message date and time.
        group_chat_id: Delete message group chat id.
        meta: Delete message meta.
        sync_ids: Delete message sync ids.
    """

    deleted_at: datetime
    group_chat_id: UUID
    sync_ids: List[UUID]
    meta: Optional[Dict[str, Any]]


class BotAPIEventDeletedData(VerifiedPayloadBaseModel):
    deleted_at: datetime
    group_chat_id: UUID
    sync_ids: List[UUID]
    meta: Optional[Dict[str, Any]]


class BotAPIEventDeletedPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.EVENT_DELETED]
    data: BotAPIEventDeletedData


class BotAPIEventDeleted(BotAPIBaseCommand):
    payload: BotAPIEventDeletedPayload = Field(..., alias="command")
    bot: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> EventDeleted:
        return EventDeleted(
            bot=BotAccount(
                id=self.bot_id,
                host=self.bot.host,
            ),
            raw_command=raw_command,
            deleted_at=self.payload.data.deleted_at,
            group_chat_id=self.payload.data.group_chat_id,
            meta=self.payload.data.meta,
            sync_ids=self.payload.data.sync_ids,
        )
