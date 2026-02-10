from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.base_command import (
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
    BotAPIChatContext,
)
from pybotx.presentation.contracts.enums import (
    BotAPISystemEventTypes,
    convert_chat_type_to_domain,
)
from pybotx.domain.models.bot_account import BotAccount
from pybotx.domain.models.chats import Chat
from pybotx.domain.models.system_events.left_from_chat import LeftFromChatEvent


class BotAPILeftFromChatData(VerifiedPayloadBaseModel):
    left_members: list[UUID]


class BotAPILeftFromChatPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.LEFT_FROM_CHAT]
    data: BotAPILeftFromChatData


class BotAPILeftFromChat(BotAPIBaseCommand):
    payload: BotAPILeftFromChatPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")

    def to_domain(self, raw_command: dict[str, Any]) -> LeftFromChatEvent:
        return LeftFromChatEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            chat=Chat(
                id=self.sender.group_chat_id,
                type=convert_chat_type_to_domain(self.sender.chat_type),
            ),
            huids=self.payload.data.left_members,
        )
