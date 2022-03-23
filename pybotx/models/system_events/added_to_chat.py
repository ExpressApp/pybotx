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
class AddedToChatEvent(BotCommandBase):
    """Event `system:added_to_chat`.

    Attributes:
        huids: List of added to chat user huids.
    """

    huids: List[UUID]
    chat: Chat


class BotAPIAddedToChatData(VerifiedPayloadBaseModel):
    added_members: List[UUID]


class BotAPIAddedToChatPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.ADDED_TO_CHAT]
    data: BotAPIAddedToChatData


class BotAPIAddedToChat(BotAPIBaseCommand):
    payload: BotAPIAddedToChatPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> AddedToChatEvent:
        return AddedToChatEvent(
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
