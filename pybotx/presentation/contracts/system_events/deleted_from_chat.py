from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.base_command import (
    BotAPIBaseCommand,
    BotAPIChatContext,
)
from pybotx.presentation.contracts.enums import (
    BotAPICommandTypes,
    BotAPISystemEventTypes,
    convert_chat_type_to_domain,
)
from pybotx.domain.models.bot_account import BotAccount
from pybotx.domain.models.chats import Chat
from pybotx.domain.models.system_events.deleted_from_chat import DeletedFromChatEvent


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
