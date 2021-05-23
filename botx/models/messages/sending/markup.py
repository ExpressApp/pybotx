"""Definition for markup attached to sent message."""

from typing import List, Optional, Type, TypeVar

from botx.models.base import BotXBaseModel
from botx.models.buttons import BubbleElement, Button, ButtonOptions, KeyboardElement

TUIElement = TypeVar("TUIElement", bound=Button)


class MessageMarkup(BotXBaseModel):
    """Collection for bubbles and keyboard with some helper methods."""

    #: bubbles that will be attached to message.
    bubbles: List[List[BubbleElement]] = []

    #: keyboard elements that will be attached to message.
    keyboard: List[List[KeyboardElement]] = []

    def add_bubble(  # noqa: WPS211
        self,
        command: str,
        label: Optional[str] = None,
        data: Optional[dict] = None,  # noqa: WPS110
        options: Optional[ButtonOptions] = None,
        *,
        new_row: bool = True,
    ) -> None:
        """Add new bubble button to markup.

        Arguments:
            command: command that will be triggered on bubble click.
            label: label that will be shown on bubble.
            data: payload that will be attached to bubble.
            options: add special effects to bubble.
            new_row: place bubble on new row or on current.
        """
        self._add_ui_element(
            ui_cls=BubbleElement,
            ui_array=self.bubbles,
            command=command,
            label=label,
            data=data,
            opts=options,
            new_row=new_row,
        )

    def add_bubble_element(
        self,
        element: BubbleElement,
        *,
        new_row: bool = True,
    ) -> None:
        """Add new button to markup from existing element.

        Arguments:
            element: existed bubble element.
            new_row: place bubble on new row or on current.
        """
        self._add_ui_element(
            ui_cls=BubbleElement,
            ui_array=self.bubbles,
            command=element.command,
            label=element.label,
            data=element.data,
            opts=element.opts,
            new_row=new_row,
        )

    def add_keyboard_button(  # noqa: WPS211
        self,
        command: str,
        label: Optional[str] = None,
        data: Optional[dict] = None,  # noqa: WPS110
        options: Optional[ButtonOptions] = None,
        *,
        new_row: bool = True,
    ) -> None:
        """Add new keyboard button to markup.

        Arguments:
            command: command that will be triggered on keyboard click.
            label: label that will be shown on keyboard button.
            data: payload that will be attached to keyboard.
            options: add special effects to keyboard button.
            new_row: place keyboard on new row or on current.
        """
        self._add_ui_element(
            ui_cls=KeyboardElement,
            ui_array=self.keyboard,
            command=command,
            label=label,
            data=data,
            opts=options,
            new_row=new_row,
        )

    def add_keyboard_button_element(
        self,
        element: KeyboardElement,
        *,
        new_row: bool = True,
    ) -> None:
        """Add new keyboard button to markup from existing element.

        Arguments:
            element: existed keyboard button element.
            new_row: place keyboard button on new row or on current.
        """
        self._add_ui_element(
            ui_cls=KeyboardElement,
            ui_array=self.keyboard,
            command=element.command,
            label=element.label,
            data=element.data,
            opts=element.opts,
            new_row=new_row,
        )

    def _add_ui_element(  # noqa: WPS211
        self,
        ui_cls: Type[TUIElement],
        ui_array: List[List[TUIElement]],
        command: str,
        label: Optional[str] = None,
        data: Optional[dict] = None,  # noqa: WPS110
        opts: Optional[ButtonOptions] = None,
        new_row: bool = True,
    ) -> None:
        """Add new button to bubble or keyboard arrays.

        Arguments:
            ui_cls: UIElement instance that should be added to array.
            ui_array: storage for ui elements.
            command: command that will be triggered on ui element click.
            label: label that will be shown on ui element.
            data: payload that will be attached to ui element.
            opts: add special effects ui element.
            new_row: place ui element on new row or on current.
        """
        element = ui_cls(
            command=command,
            label=label,
            data=(data or {}),
            opts=(opts or ButtonOptions()),
        )

        if new_row:
            ui_array.append([element])
            return

        if not ui_array:
            ui_array.append([])

        ui_array[-1].append(element)
