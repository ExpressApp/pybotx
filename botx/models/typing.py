"""Aliases for complex types from `typing` for models."""

from typing import List, Literal, Union
from uuid import UUID

from botx.models.buttons import BubbleElement, KeyboardElement
from botx.models.enums import Recipients

BubblesRow = List[BubbleElement]
BubbleMarkup = List[BubblesRow]

KeyboardRow = List[KeyboardElement]
KeyboardMarkup = List[KeyboardRow]

AvailableRecipients = Union[List[UUID], Literal[Recipients.all]]
