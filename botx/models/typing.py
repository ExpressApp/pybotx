"""Aliases for complex types from `typing` for models."""

from typing import List, Union
from uuid import UUID

from botx.models.buttons import BubbleElement, KeyboardElement

try:
    from typing import Literal  # noqa: WPS433
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS433, WPS440, F401

BubblesRow = List[BubbleElement]
BubbleMarkup = List[BubblesRow]

KeyboardRow = List[KeyboardElement]
KeyboardMarkup = List[KeyboardRow]

AvailableRecipients = Union[List[UUID], Literal["all"]]
