"""Pydantic models for bubbles and keyboard buttons."""

from typing import Optional

from pydantic import BaseModel, validator


class ButtonOptions(BaseModel):
    """Extra options for buttons, like disabling output by tap."""

    silent: bool = True
    """if True then text won't shown for user in messenger."""


class Button(BaseModel):
    """Base class for ui element like bubble or keyboard button."""

    command: str
    """command that will be triggered by click on the element."""
    label: Optional[str] = None
    """text that will be shown on the element."""
    data: dict = {}
    """extra payload that will be stored in button and then received in new message."""
    opts: ButtonOptions = ButtonOptions()
    """options for button."""

    @validator("label", always=True)
    def label_as_command_if_none(
        cls, value: Optional[str], values: dict,
    ) -> str:
        """Return command as label if it is `None`.

        Arguments:
            value: value that should be checked.
            values: all other values checked before.

        Returns:
            Label for button.
        """
        return value or values["command"]

    @validator("data", always=True)
    def add_ui_flag_to_data(cls, value: dict) -> dict:
        """Return command data with set UI flag.

        Arguments:
            value: data passed to bot.

        Returns:
            Passed data with set "ui" flag to True if it wasn't set already.
        """
        value.setdefault("ui", True)
        return value


class BubbleElement(Button):
    """Bubble buttons that is shown under messages."""


class KeyboardElement(Button):
    """Keyboard buttons that are placed instead of real keyboard."""
