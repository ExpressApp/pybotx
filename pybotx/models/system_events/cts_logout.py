from dataclasses import dataclass
from typing import Any, Dict, Literal
from uuid import UUID

from pydantic import Field

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.base_command import (
    BaseBotAPIContext,
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
    BotCommandBase,
)
from pybotx.models.bot_account import BotAccount
from pybotx.models.enums import BotAPISystemEventTypes


@dataclass
class CTSLogoutEvent(BotCommandBase):
    """Event `system:cts_logout`.

    Attributes:
        huid: user ID.
    """

    huid: UUID


class BotAPICTSLogoutData(VerifiedPayloadBaseModel):
    user_huid: UUID


class BotAPICTSLogoutPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.CTS_LOGOUT]
    data: BotAPICTSLogoutData


class BotAPICTSLogout(BotAPIBaseCommand):
    payload: BotAPICTSLogoutPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> CTSLogoutEvent:
        return CTSLogoutEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            huid=self.payload.data.user_huid,
        )
