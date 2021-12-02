from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import UUID

from pydantic import Field

from botx.bot.api.commands.base import BotAPIBaseCommand, BotAPIChatContext
from botx.bot.api.enums import BotAPICommandTypes
from botx.bot.models.commands.base import BotCommandBase
from botx.bot.models.commands.chat import Chat
from botx.shared_models.api_base import VerifiedPayloadBaseModel
from botx.shared_models.chat_types import convert_chat_type_to_domain

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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
            bot_id=self.bot_id,
            raw_command=raw_command,
            huids=self.payload.data.deleted_members,
            chat=Chat(
                id=self.sender.group_chat_id,
                type=convert_chat_type_to_domain(self.sender.chat_type),
                host=self.sender.host,
            ),
        )
