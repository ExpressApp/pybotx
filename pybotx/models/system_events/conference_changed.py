from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
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
from pybotx.models.enums import (
    BotAPIConferenceLinkTypes,
    BotAPISystemEventTypes,
    ConferenceLinkTypes,
    convert_conference_link_type_to_domain,
)


@dataclass
class ConferenceChangedEvent(BotCommandBase):
    """Event `system:conference_changed`.

    Attributes:
        access_code: access code for conference.
        actor: who changes conference.
        added_users: added users to conference.
        admins: admins conference.
        call_id: id conference.
        deleted_users: deleted users to conference.
        end_at: end conference.
        link: conference link.
        link_id: conference link id.
        link_type: link type on conference (public|trusts|corporate|server).
        members: list members.
        name: name conference.
        operation: operation.
        sip_number: sip number conference.
        start_at: end conference.
    """

    access_code: Optional[str]
    actor: Optional[UUID]
    added_users: List[UUID]
    admins: List[UUID]
    call_id: UUID
    deleted_users: List[UUID]
    end_at: Optional[datetime]
    link: str
    link_id: UUID
    link_type: ConferenceLinkTypes
    members: List[UUID]
    name: str
    operation: str
    sip_number: int
    start_at: datetime


class BotAPIConferenceChangedData(VerifiedPayloadBaseModel):
    access_code: Optional[str]
    actor: Optional[UUID]
    added_users: List[UUID]
    admins: List[UUID]
    call_id: UUID
    deleted_users: List[UUID]
    end_at: Optional[datetime]
    link: str
    link_id: UUID
    link_type: BotAPIConferenceLinkTypes
    members: List[UUID]
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

    def to_domain(self, raw_command: Dict[str, Any]) -> ConferenceChangedEvent:
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
