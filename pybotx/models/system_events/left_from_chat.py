from dataclasses import dataclass
from typing import Any, Dict, List, Literal
from uuid import UUID

from pydantic import Field

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
    BotAPIChatContext,
    BotCommandBase,
)
from pybotx.models.bot_account import BotAccount
from pybotx.models.chats import Chat
from pybotx.models.enums import BotAPISystemEventTypes, convert_chat_type_to_domain


@dataclass
class LeftFromChatEvent(BotCommandBase):
    """Event `system:left_from_chat`.

    Attributes:
        huids: List of left from chat user huids.
    """

    huids: List[UUID]
    chat: Chat


class BotAPILeftFromChatData(VerifiedPayloadBaseModel):
    left_members: List[UUID]


class BotAPILeftFromChatPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.LEFT_FROM_CHAT]
    data: BotAPILeftFromChatData


class BotAPILeftFromChat(BotAPIBaseCommand):
    payload: BotAPILeftFromChatPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> LeftFromChatEvent:
        return LeftFromChatEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            huids=self.payload.data.left_members,
            chat=Chat(
                id=self.sender.group_chat_id,
                type=convert_chat_type_to_domain(self.sender.chat_type),
            ),
        )
