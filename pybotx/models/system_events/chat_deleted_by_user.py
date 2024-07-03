from dataclasses import dataclass
from typing import Any, Dict, Literal
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
class ChatDeletedByUserEvent(BotCommandBase):
    """Event `system:chat_deleted_by_user`.

    Attributes:
        sync_id: Event sync id.
        chat_id: Deleted chat id.
        huid: huid of the deleter.
    """

    sync_id: UUID
    chat_id: UUID
    huid: UUID


class BotAPIChatDeletedByUserData(VerifiedPayloadBaseModel):
    user_huid: UUID
    group_chat_id: UUID


class BotAPIChatDeletedByUserPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.CHAT_DELETED_BY_USER]
    data: BotAPIChatDeletedByUserData


class BotAPIChatDeletedByUser(BotAPIBaseCommand):
    payload: BotAPIChatDeletedByUserPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> ChatDeletedByUserEvent:
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
