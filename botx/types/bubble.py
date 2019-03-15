from typing import Optional

from .base import BotXType


class BubbleElement(BotXType):
    command: str
    label: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.label = self.label or self.command
