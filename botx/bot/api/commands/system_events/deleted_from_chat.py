from typing import Any, Dict, List
from uuid import UUID

from pydantic import Field

from botx.bot.api.commands.base import BotAPIBaseCommand, BotAPIChatEventSender
from botx.bot.api.enums import BotAPICommandTypes
from botx.bot.models.commands.system_events.deleted_from_chat import (
    DeletedFromChatEvent,
)
from botx.shared_models.api_base import VerifiedPayloadBaseModel

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotAPIDeletedFromChatData(VerifiedPayloadBaseModel):
    deleted_members: List[UUID]


class BotAPIDeletedFromChatPayload(VerifiedPayloadBaseModel):
    body: Literal["system:deleted_from_chat"] = "system:deleted_from_chat"
    command_type: Literal[BotAPICommandTypes.SYSTEM]
    data: BotAPIDeletedFromChatData


class BotAPIDeletedFromChat(BotAPIBaseCommand):
    payload: BotAPIDeletedFromChatPayload = Field(..., alias="command")
    sender: BotAPIChatEventSender = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> DeletedFromChatEvent:
        return DeletedFromChatEvent(
            bot_id=self.bot_id,
            raw_command=raw_command,
            huids=self.payload.data.deleted_members,
        )
