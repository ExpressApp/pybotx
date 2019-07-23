from typing import Any, Dict, List, Optional

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


class NotificationOpts(BotXType):
    send: bool = True
    force_dnd: bool = False
