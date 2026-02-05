from dataclasses import dataclass
from typing import Any, Literal
from uuid import UUID

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIChatContext,
    BotCommandBase,
)
from pybotx.models.bot_account import BotAccount
from pybotx.models.chats import Chat
from pybotx.models.enums import (
    BotAPICommandTypes,
    BotAPISystemEventTypes,
    convert_chat_type_to_domain,
)
from pydantic import Field


@dataclass(slots=True)
class DeletedFromChatEvent(BotCommandBase):
    """Event `system:deleted_from_chat`.

    Attributes:
        huids: List of deleted from chat user huids.
        chat_id: Chat where the user was deleted from.
    """

    huids: list[UUID]
    chat: Chat


class BotAPIDeletedFromChatData(VerifiedPayloadBaseModel):
    deleted_members: list[UUID]


class BotAPIDeletedFromChatPayload(VerifiedPayloadBaseModel):
    body: Literal[BotAPISystemEventTypes.DELETED_FROM_CHAT]
    command_type: Literal[BotAPICommandTypes.SYSTEM]
    data: BotAPIDeletedFromChatData


class BotAPIDeletedFromChat(BotAPIBaseCommand):
    payload: BotAPIDeletedFromChatPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")

    def to_domain(self, raw_command: dict[str, Any]) -> DeletedFromChatEvent:
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
