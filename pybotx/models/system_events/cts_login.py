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
class CTSLoginEvent(BotCommandBase):
    """Event `system:cts_login`.

    Attributes:
        huid: user ID.
    """

    huid: UUID


class BotAPICTSLoginData(VerifiedPayloadBaseModel):
    user_huid: UUID


class BotAPICTSLoginPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.CTS_LOGIN]
    data: BotAPICTSLoginData


class BotAPICTSLogin(BotAPIBaseCommand):
    payload: BotAPICTSLoginPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> CTSLoginEvent:
        return CTSLoginEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            huid=self.payload.data.user_huid,
        )
