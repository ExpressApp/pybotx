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
class CTSLoginEvent(BotCommandBase):
    """Event `system:cts_login`.

    Attributes:
        huid: user ID.
    """

    huid: UUID


class BotAPICTSLoginData(VerifiedPayloadBaseModel):
    user_huid: UUID


class BotAPICTSLoginPayload(VerifiedPayloadBaseModel):
    body: Literal["system:cts_login"] = "system:cts_login"
    command_type: Literal[BotAPICommandTypes.SYSTEM]
    data: BotAPICTSLoginData


class BotAPICTSLogin(BotAPIBaseCommand):
    payload: BotAPICTSLoginPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> CTSLoginEvent:
        return CTSLoginEvent(
            bot_id=self.bot_id,
            host=self.sender.host,
            raw_command=raw_command,
            huid=self.payload.data.user_huid,
        )