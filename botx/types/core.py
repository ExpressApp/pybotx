from typing import Any, Dict, List, Optional
from uuid import UUID

from .base import BotXType


class CommandUIElement(BotXType):
    type: str
    label: str
    order: Optional[int] = None
    value: Optional[Any] = None
    name: Optional[str] = None
    disabled: Optional[bool] = None


class MenuCommand(BotXType):
    description: str
    body: str
    name: str
    options: Dict[str, Any] = {}
    elements: List[CommandUIElement] = []


class SyncID(UUID):
    def __init__(self, obj, **data):
        if isinstance(obj, UUID):
            super().__init__(str(obj), **data)
        else:
            super().__init__(obj, **data)
