from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase


@dataclass(slots=True)
class ConferenceDeletedEvent(BotCommandBase):
    """Event `system:conference_deleted`.

    Attributes:
        call_id: id conference.
    """

    call_id: UUID
