from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal
from collections.abc import Iterator

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.errors import InvalidMarkupError


class ButtonTextAlign(Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


@dataclass(slots=True)
class Button:
    """
    Button object.

    :param label: Button name.
    :param command: Button command (required if no `link` is undefined).
    :param data: Button body that will be sent as command parameters
        when the button is clicked.
    :param text_color: Button text color.
    :param background_color: Bubbles background color.
    :param align (default CENTER): Text alignment left | center | right
    :param silent: If true, then when the button is pressed
        the message will not be sent to the chat, it will be sent in the background.
    :param width_ratio: Horizontal button size.
    :param alert: Button notification text.
    :param process_on_client: Execute process on client.
    :param link: URL to resource.

    :raises InvalidMarkupError: If `command` is missing.
        `command` is optional only if `link` is not undefined.
    """

    label: str
    command: Missing[str] = Undefined
    data: dict[str, Any] = field(default_factory=dict)
    text_color: Missing[str] = Undefined
    background_color: Missing[str] = Undefined
    align: ButtonTextAlign = ButtonTextAlign.CENTER

    silent: bool = True  # BotX has `False` as default, so Missing type can't be used
    width_ratio: Missing[int] = Undefined
    alert: Missing[str] = Undefined
    process_on_client: Missing[bool] = Undefined
    link: Missing[str] = Undefined

    def __post_init__(self) -> None:
        if self.command is Undefined and self.link is Undefined:
            raise InvalidMarkupError("Either 'command' or 'link' must be provided")


ButtonRow = list[Button]


class BaseMarkup:
    def __init__(self, buttons: list[ButtonRow] | None = None) -> None:
        self._buttons = buttons or []

    def __iter__(self) -> Iterator[ButtonRow]:
        return iter(self._buttons)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseMarkup):
            raise NotImplementedError

        # https://github.com/wemake-services/wemake-python-styleguide/issues/2172
        return self._buttons == other._buttons

    def __repr__(self) -> str:
        buttons = []

        for idx, row in enumerate(self._buttons, start=1):
            row_buttons_strings = [
                f"{button.label} ({button.command})" for button in row
            ]
            row_string = " | ".join(row_buttons_strings)
            buttons.append(f"row {idx}: {row_string}")

        return "\n".join(buttons)

    def add_built_button(self, button: Button, new_row: bool = True) -> None:
        if new_row:
            self._buttons.append([button])
            return

        if not self._buttons:
            self._buttons.append([])

        self._buttons[-1].append(button)

    def add_button(
        self,
        label: str,
        command: Missing[str] = Undefined,
        data: dict[str, Any] | None = None,
        text_color: Missing[str] = Undefined,
        background_color: Missing[str] = Undefined,
        align: ButtonTextAlign = ButtonTextAlign.CENTER,
        silent: bool = True,
        width_ratio: Missing[int] = Undefined,
        alert: Missing[str] = Undefined,
        process_on_client: Missing[bool] = Undefined,
        link: Missing[str] = Undefined,
        new_row: bool = True,
    ) -> None:
        """Add button.

        :param label: Button name.
        :param command: Button command (required if no `link` is undefined).
        :param data: Button body that will be sent as command parameters
            when the button is clicked.
        :param text_color: Button text color.
        :param background_color: Bubbles background color.
        :param align: Text alignment left | center | right
        :param silent: If true, then when the button is pressed
            the message will not be sent to the chat, it will be sent in the background.
        :param width_ratio: Horizontal button size.
        :param alert: Button notification text.
        :param process_on_client: Execute process on client.
        :param link: URL to resource.
        :param new_row: Move the next button to a new row.

        :raises InvalidMarkupError: If `command` is missing.
            `command` is optional only if `link` is undefined.
        """

        if link is Undefined and command is Undefined:
            raise InvalidMarkupError("Command arg is required if link is undefined.")

        button = Button(
            command=command,
            label=label,
            data=data or {},
            text_color=text_color,
            background_color=background_color,
            align=align,
            silent=silent,
            width_ratio=width_ratio,
            alert=alert,
            process_on_client=process_on_client,
            link=link,
        )
        self.add_built_button(button, new_row=new_row)

    def add_row(self, button_row: ButtonRow) -> None:
        self._buttons.append(button_row)


class BubbleMarkup(BaseMarkup):
    """Class for managing inline message buttons."""


class KeyboardMarkup(BaseMarkup):
    """Class for managing keyboard message buttons."""


Markup = BubbleMarkup | KeyboardMarkup
