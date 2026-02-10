from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase


@dataclass(slots=True)
class CTSLoginEvent(BotCommandBase):
    """Event `system:cts_login`.

    Attributes:
        huid: user ID.
    """

    huid: UUID
