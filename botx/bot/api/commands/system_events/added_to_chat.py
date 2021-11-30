from typing import Any, Dict, List
from uuid import UUID

from pydantic import Field

from botx.bot.api.commands.base import BotAPIBaseCommand, BotAPIChatContext
from botx.bot.api.enums import BotAPICommandTypes
from botx.bot.models.commands.chat import Chat
from botx.bot.models.commands.system_events.added_to_chat import AddedToChatEvent
from botx.shared_models.api_base import VerifiedPayloadBaseModel
from botx.shared_models.chat_types import convert_chat_type_to_domain

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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
            raw_command=raw_command,
            huids=self.payload.data.added_members,
            chat=Chat(
                id=self.sender.group_chat_id,
                type=convert_chat_type_to_domain(self.sender.chat_type),
                host=self.sender.host,
            ),
        )
