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
from pybotx.domain.models.system_events.conference_created import (
    ConferenceCreatedEvent,
)


class BotAPIConferenceCreatedData(VerifiedPayloadBaseModel):
    call_id: UUID


class BotAPIConferenceCreatedPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.CONFERENCE_CREATED]
    data: BotAPIConferenceCreatedData


class BotAPIConferenceCreated(BotAPIBaseCommand):
    payload: BotAPIConferenceCreatedPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: dict[str, Any]) -> ConferenceCreatedEvent:
        return ConferenceCreatedEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            call_id=self.payload.data.call_id,
        )
