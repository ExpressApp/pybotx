from typing import Any, Literal
from uuid import UUID

from pydantic import ConfigDict, Field

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
from pybotx.domain.models.system_events.user_joined_to_chat import JoinToChatEvent


class BotAPIJoinToChatData(VerifiedPayloadBaseModel):
    """Data model for user joined to chat event."""

    added_members: list[UUID]


class BotAPIJoinToChatPayload(BotAPIBaseSystemEventPayload):
    """Payload model for user joined to chat event."""

    body: Literal[BotAPISystemEventTypes.JOIN_TO_CHAT]
    data: BotAPIJoinToChatData


class BotAPIJoinToChat(BotAPIBaseCommand):
    """API model for user joined to chat event."""

    payload: BotAPIJoinToChatPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")

    def to_domain(self, raw_command: dict[str, Any]) -> JoinToChatEvent:
        return JoinToChatEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            huids=self.payload.data.added_members,
            chat=Chat(
                id=self.sender.group_chat_id,
                type=convert_chat_type_to_domain(self.sender.chat_type),
            ),
        )

    model_config = ConfigDict(populate_by_name=True)
