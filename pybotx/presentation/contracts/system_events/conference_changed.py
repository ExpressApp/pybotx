from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.base_command import (
    BaseBotAPIContext,
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
)
from pybotx.presentation.contracts.enums import (
    BotAPIConferenceLinkTypes,
    BotAPISystemEventTypes,
    convert_conference_link_type_to_domain,
)
from pybotx.domain.models.bot_account import BotAccount
from pybotx.domain.models.system_events.conference_changed import (
    ConferenceChangedEvent,
)


class BotAPIConferenceChangedData(VerifiedPayloadBaseModel):
    access_code: str | None
    actor: UUID | None
    added_users: list[UUID]
    admins: list[UUID]
    call_id: UUID
    deleted_users: list[UUID]
    end_at: datetime | None
    link: str
    link_id: UUID
    link_type: BotAPIConferenceLinkTypes
    members: list[UUID]
    name: str
    operation: str
    sip_number: int
    start_at: datetime


class BotAPIConferenceChangedPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.CONFERENCE_CHANGED]
    data: BotAPIConferenceChangedData


class BotAPIConferenceChanged(BotAPIBaseCommand):
    payload: BotAPIConferenceChangedPayload = Field(..., alias="command")
    sender: BaseBotAPIContext = Field(..., alias="from")

    def to_domain(self, raw_command: dict[str, Any]) -> ConferenceChangedEvent:
        return ConferenceChangedEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            access_code=self.payload.data.access_code,
            actor=self.payload.data.actor,
            added_users=self.payload.data.added_users,
            admins=self.payload.data.admins,
            call_id=self.payload.data.call_id,
            deleted_users=self.payload.data.deleted_users,
            end_at=self.payload.data.end_at,
            link=self.payload.data.link,
            link_id=self.payload.data.link_id,
            link_type=convert_conference_link_type_to_domain(
                self.payload.data.link_type,
            ),
            members=self.payload.data.members,
            name=self.payload.data.name,
            operation=self.payload.data.operation,
            sip_number=self.payload.data.sip_number,
            start_at=self.payload.data.start_at,
        )
