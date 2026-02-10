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
from pybotx.domain.models.system_events.chat_deleted_by_user import (
    ChatDeletedByUserEvent,
)


class BotAPIChatDeletedByUserData(VerifiedPayloadBaseModel):
    user_huid: UUID
    group_chat_id: UUID


class BotAPIChatDeletedByUserPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.CHAT_DELETED_BY_USER]
    data: BotAPIChatDeletedByUserData


class BotAPIChatDeletedByUser(BotAPIBaseCommand):
    payload: BotAPIChatDeletedByUserPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: dict[str, Any]) -> ChatDeletedByUserEvent:
        return ChatDeletedByUserEvent(
            sync_id=self.sync_id,
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            chat_id=self.payload.data.group_chat_id,
            huid=self.payload.data.user_huid,
            raw_command=raw_command,
        )
