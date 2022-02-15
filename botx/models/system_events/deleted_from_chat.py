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
class DeletedFromChatEvent(BotCommandBase):
    """Event `system:deleted_from_chat`.

    Attributes:
        huids: List of deleted from chat user huids.
        chat_id: Chat where the user was deleted from.
    """

    huids: List[UUID]
    chat: Chat


class BotAPIDeletedFromChatData(VerifiedPayloadBaseModel):
    deleted_members: List[UUID]


class BotAPIDeletedFromChatPayload(VerifiedPayloadBaseModel):
    body: Literal["system:deleted_from_chat"] = "system:deleted_from_chat"
    command_type: Literal[BotAPICommandTypes.SYSTEM]
    data: BotAPIDeletedFromChatData


class BotAPIDeletedFromChat(BotAPIBaseCommand):
    payload: BotAPIDeletedFromChatPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> DeletedFromChatEvent:
        return DeletedFromChatEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            huids=self.payload.data.deleted_members,
            chat=Chat(
                id=self.sender.group_chat_id,
                type=convert_chat_type_to_domain(self.sender.chat_type),
            ),
        )
