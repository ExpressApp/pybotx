from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import UUID

from pydantic import Field

from botx.models.api_base import VerifiedPayloadBaseModel
from botx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIChatContext,
    BotCommandBase,
)
from botx.models.chats import Chat
from botx.models.enums import BotAPICommandTypes, convert_chat_type_to_domain

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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


class BotAPIAddedToChatPayload(VerifiedPayloadBaseModel):
    body: Literal["system:added_to_chat"] = "system:added_to_chat"
    command_type: Literal[BotAPICommandTypes.SYSTEM]
    data: BotAPIAddedToChatData
    metadata: Dict[str, Any]


class BotAPIAddedToChat(BotAPIBaseCommand):
    payload: BotAPIAddedToChatPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> AddedToChatEvent:
        return AddedToChatEvent(
            bot_id=self.bot_id,
            host=self.sender.host,
            raw_command=raw_command,
            huids=self.payload.data.added_members,
            chat=Chat(
                id=self.sender.group_chat_id,
                type=convert_chat_type_to_domain(self.sender.chat_type),
            ),
        )
