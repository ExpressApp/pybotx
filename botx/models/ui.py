from typing import Any, Optional

from .base import BotXType


class UIElement(BotXType):
    command: str
    label: Optional[str] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.label = self.label or self.command


class BubbleElement(UIElement):
    pass


class KeyboardElement(UIElement):
    pass
