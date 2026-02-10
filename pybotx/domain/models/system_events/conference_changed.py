from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase
from pybotx.domain.models.enums import ConferenceLinkTypes


@dataclass(slots=True)
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

    access_code: str | None
    actor: UUID | None
    added_users: list[UUID]
    admins: list[UUID]
    call_id: UUID
    deleted_users: list[UUID]
    end_at: datetime | None
    link: str
    link_id: UUID
    link_type: ConferenceLinkTypes
    members: list[UUID]
    name: str
    operation: str
    sip_number: int
    start_at: datetime
