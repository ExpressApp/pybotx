"""Pydantic models for bubbles and keyboard buttons."""

from typing import Optional

from pydantic import BaseModel, validator


class ButtonOptions(BaseModel):
    """Extra options for buttons, like disabling output by tap."""

    #: if True then text won't shown for user in messenger.
    silent: bool = True


class Button(BaseModel):
    """Base class for ui element like bubble or keyboard button."""

    #: command that will be triggered by click on the element.
    command: str

    #: text that will be shown on the element.
    label: Optional[str] = None

    #: extra payload that will be stored in button and then received in new message.
    data: dict = {}  # noqa: WPS110

    #: options for button.
    opts: ButtonOptions = ButtonOptions()

    @validator("label", always=True)
    def label_as_command_if_none(
        cls, label: Optional[str], values: dict,  # noqa: N805, WPS110
    ) -> str:
        """Return command as label if it is `None`.

        Arguments:
            cls: passed button class.
            label: value that should be checked.
            values: all other validated_values checked before.

        Returns:
            Label for button.
        """
        return label or values["command"]

    @validator("data", always=True)
    def add_ui_flag_to_data(cls, button_data: dict) -> dict:  # noqa: N805
        """Return command data with set UI flag.

        Arguments:
            cls: passed button class.
            button_data: data passed to bot.

        Returns:
            Passed data with set "ui" flag to True if it wasn't set already.
        """
        button_data.setdefault("ui", True)
        return button_data


class BubbleElement(Button):
    """Bubble buttons that is shown under messages."""


class KeyboardElement(Button):
    """Keyboard buttons that are placed instead of real keyboard."""
