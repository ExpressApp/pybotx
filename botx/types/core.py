from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from .base import BotXType


class StatusEnum(str, Enum):
    ok: str = "ok"
    error: str = "error"


class CommandUIElement(BotXType):
    type: str
    label: str
    order: Optional[int] = None
    value: Optional[Any] = None
    disabled: Optional[bool] = None


class MenuCommand(BotXType):
    description: str
    body: str
    name: str
    options: Dict[str, Any] = {}
    elements: List[CommandUIElement] = []


class SyncID(UUID):
    pass
