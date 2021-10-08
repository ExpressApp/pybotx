from typing import Any, Dict, List
from uuid import UUID

from pydantic import Field

from botx.bot.api.commands.base import BotAPIBaseCommand, BotAPIChatEventSender
from botx.bot.api.enums import BotAPICommandTypes
from botx.bot.models.commands.system_events.added_to_chat import AddedToChatEvent
from botx.shared_models.api_base import VerifiedPayloadBaseModel

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
    sender: BotAPIChatEventSender = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> AddedToChatEvent:
        return AddedToChatEvent(
            bot_id=self.bot_id,
            raw_command=raw_command,
            huids=self.payload.data.added_members,
        )
