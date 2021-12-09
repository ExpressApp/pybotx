from dataclasses import dataclass
from typing import Any, Dict
from uuid import UUID

from pydantic import Field

from botx.models.api_base import VerifiedPayloadBaseModel
from botx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIChatContext,
    BotCommandBase,
)
from botx.models.bot_recipient import BotRecipient
from botx.models.enums import BotAPICommandTypes

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class SmartAppEvent(BotCommandBase):
    """Event `system:smartapp_event`.

    Attributes:
        ref: Unique request id.
        smartapp_id: also personnel chat_id.
        data: Payload.
        opts: Request options.
        smartapp_api_version: Protocol version.
    """

    ref: UUID
    smartapp_id: UUID
    data: Dict[str, Any]  # noqa: WPS110
    opts: Dict[str, Any]
    smartapp_api_version: int


class BotAPISmartAppData(VerifiedPayloadBaseModel):
    ref: UUID
    smartapp_id: UUID
    data: Dict[str, Any]  # noqa: WPS110
    opts: Dict[str, Any]
    smartapp_api_version: int


class BotAPISmartAppPayload(VerifiedPayloadBaseModel):
    body: Literal["system:smartapp_event"] = "system:smartapp_event"
    command_type: Literal[BotAPICommandTypes.SYSTEM]
    data: BotAPISmartAppData
    metadata: Dict[str, Any]


class BotAPISmartAppEvent(BotAPIBaseCommand):
    payload: BotAPISmartAppPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")
    # TODO: files

    def to_domain(self, raw_command: Dict[str, Any]) -> SmartAppEvent:
        return SmartAppEvent(
            bot=BotRecipient(id=self.bot_id, host=self.sender.host),
            raw_command=raw_command,
            ref=self.payload.data.ref,
            smartapp_id=self.payload.data.smartapp_id,
            data=self.payload.data.data,
            opts=self.payload.data.opts,
            smartapp_api_version=self.payload.data.smartapp_api_version,
        )
