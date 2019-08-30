from typing import Any, List, Optional, Type, TypeVar

from .base import BotXType


class UIElement(BotXType):
    command: str
    label: Optional[str] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.label = self.label or self.command


TUIElement = TypeVar("TUIElement", bound=UIElement)


class BubbleElement(UIElement):
    pass


class KeyboardElement(UIElement):
    pass


def add_ui_element(
    ui_cls: Type["TUIElement"],
    ui_array: List[List["TUIElement"]],
    command: str,
    label: Optional[str] = None,
    *,
    new_row: bool = True,
) -> None:
    element = ui_cls(command=command, label=label)

    if new_row:
        ui_array.append([element])
    else:
        ui_array[-1].append(element)
