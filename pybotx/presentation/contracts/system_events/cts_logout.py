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
from pybotx.domain.models.system_events.cts_logout import CTSLogoutEvent


class BotAPICTSLogoutData(VerifiedPayloadBaseModel):
    user_huid: UUID


class BotAPICTSLogoutPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.CTS_LOGOUT]
    data: BotAPICTSLogoutData


class BotAPICTSLogout(BotAPIBaseCommand):
    payload: BotAPICTSLogoutPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: dict[str, Any]) -> CTSLogoutEvent:
        return CTSLogoutEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            huid=self.payload.data.user_huid,
        )
