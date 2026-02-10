from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase


@dataclass(slots=True)
class CTSLogoutEvent(BotCommandBase):
    """Event `system:cts_logout`.

    Attributes:
        huid: user ID.
    """

    huid: UUID
