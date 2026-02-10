from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase


@dataclass(slots=True)
class ConferenceCreatedEvent(BotCommandBase):
    """Event `system:conference_created`.

    Attributes:
        call_id: id conference.
    """

    call_id: UUID
