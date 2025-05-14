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
class ConferenceCreatedEvent(BotCommandBase):
    """Event `system:conference_created`.

    Attributes:
        call_id: id conference.
    """

    call_id: UUID


class BotAPIConferenceCreatedData(VerifiedPayloadBaseModel):
    call_id: UUID


class BotAPIConferenceCreatedPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.CONFERENCE_CREATED]
    data: BotAPIConferenceCreatedData


class BotAPIConferenceCreated(BotAPIBaseCommand):
    payload: BotAPIConferenceCreatedPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> ConferenceCreatedEvent:
        return ConferenceCreatedEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            call_id=self.payload.data.call_id,
        )
