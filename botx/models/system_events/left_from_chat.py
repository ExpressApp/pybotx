from dataclasses import dataclass
from typing import Any, Dict, List, Literal
from uuid import UUID

from pydantic import Field

from botx.models.api_base import VerifiedPayloadBaseModel
from botx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIChatContext,
    BotCommandBase,
)
from botx.models.bot_account import BotAccount
from botx.models.chats import Chat
from botx.models.enums import BotAPICommandTypes, convert_chat_type_to_domain


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


class BotAPILeftFromChatPayload(VerifiedPayloadBaseModel):
    body: Literal["system:left_from_chat"] = "system:left_from_chat"
    command_type: Literal[BotAPICommandTypes.SYSTEM]
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
