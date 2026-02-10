from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.base_command import (
    BaseBotAPIContext,
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
)
from pybotx.presentation.contracts.enums import BotAPISystemEventTypes
from pybotx.domain.models.bot_account import BotAccount
from pybotx.domain.models.system_events.event_delete import EventDeleted


class BotAPIEventDeletedData(VerifiedPayloadBaseModel):
    deleted_at: datetime
    group_chat_id: UUID
    sync_ids: list[UUID]
    meta: dict[str, Any] | None


class BotAPIEventDeletedPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.EVENT_DELETED]
    data: BotAPIEventDeletedData


class BotAPIEventDeleted(BotAPIBaseCommand):
    payload: BotAPIEventDeletedPayload = Field(..., alias="command")
    bot: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: dict[str, Any]) -> EventDeleted:
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
