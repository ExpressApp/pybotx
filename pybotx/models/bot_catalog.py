from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class BotsListItem:
    """Bot from list of bots.

    Attributes:
        id: Bot user huid.
        name: Bot name.
        description: Bot description.
        avatar: Bot avatar url.
        enabled: Is the SmartApp enabled or not.
    """

    id: UUID
    name: str
    description: str
    avatar: Optional[str]
    enabled: bool
