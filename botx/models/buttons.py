"""Pydantic models for bubbles and keyboard buttons."""

from typing import Optional

from pydantic import validator

from botx.models.base import BotXBaseModel
from botx.models.enums import ButtonHandlerTypes


class ButtonOptions(BotXBaseModel):
    """Extra options for buttons, like disabling output by tap."""

    #: if True then text won't shown for user in messenger.
    silent: bool = True

    #: button width weight (the more weight, the more occupied space).
    h_size: int = 1

    #: show toast with `alert_text` when user press the button
    show_alert: bool = False

    #: text to be shown in toast (show command body if `alert_text` is `None`).
    alert_text: Optional[str] = None

    #: platform, that handle command from markup. If `bot` - command should be send
    # to bot, else(`client`) should be executed by client.
    handler: ButtonHandlerTypes = ButtonHandlerTypes.bot

    @validator("h_size")
    def h_size_should_be_positive(cls, h_size: int) -> int:  # noqa: N805
        """Validate that `h_size` is positive integer.

        Arguments:
            h_size: width weight for validation.

        Returns:
            Validated `h_size`.

        Raises:
            ValueError: if `h_size` is not valid.
        """
        if h_size < 1:
            raise ValueError("h_size should be positive integer")

        return h_size


class Button(BotXBaseModel):
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
        cls,
        label: Optional[str],
        values: dict,  # noqa: N805, WPS110
    ) -> str:
        """Return command as label if it is `None`.

        Arguments:
            label: value that should be checked.
            values: all other validated_values checked before.

        Returns:
            Label for button.
        """
        if label is None:
            return values["command"]

        return label


class BubbleElement(Button):
    """Bubble buttons that is shown under messages."""


class KeyboardElement(Button):
    """Keyboard buttons that are placed instead of real keyboard."""
