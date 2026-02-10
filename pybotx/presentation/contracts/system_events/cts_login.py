from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.base_command import (
    BaseBotAPIContext,
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
)
from pybotx.presentation.contracts.enums import BotAPISystemEventTypes
from pybotx.domain.models.bot_account import BotAccount
from pybotx.domain.models.system_events.cts_login import CTSLoginEvent


class BotAPICTSLoginData(VerifiedPayloadBaseModel):
    user_huid: UUID


class BotAPICTSLoginPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.CTS_LOGIN]
    data: BotAPICTSLoginData


class BotAPICTSLogin(BotAPIBaseCommand):
    payload: BotAPICTSLoginPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: dict[str, Any]) -> CTSLoginEvent:
        return CTSLoginEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            huid=self.payload.data.user_huid,
        )
