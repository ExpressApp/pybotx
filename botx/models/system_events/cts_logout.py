from dataclasses import dataclass
from typing import Any, Dict
from uuid import UUID

from pydantic import Field

from botx.models.api_base import VerifiedPayloadBaseModel
from botx.models.base_command import (
    BaseBotAPIContext,
    BotAPIBaseCommand,
    BotCommandBase,
)
from botx.models.enums import BotAPICommandTypes

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class CTSLogoutEvent(BotCommandBase):
    """Event `system:cts_logout`.

    Attributes:
        huid: user ID.
    """

    huid: UUID


class BotAPICTSLogoutData(VerifiedPayloadBaseModel):
    user_huid: UUID


class BotAPICTSLogoutPayload(VerifiedPayloadBaseModel):
    body: Literal["system:cts_logout"] = "system:cts_logout"
    command_type: Literal[BotAPICommandTypes.SYSTEM]
    data: BotAPICTSLogoutData


class BotAPICTSLogout(BotAPIBaseCommand):
    payload: BotAPICTSLogoutPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> CTSLogoutEvent:
        return CTSLogoutEvent(
            bot_id=self.bot_id,
            host=self.sender.host,
            raw_command=raw_command,
            huid=self.payload.data.user_huid,
        )