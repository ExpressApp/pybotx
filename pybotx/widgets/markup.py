from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, TypeVar

from pybotx.missing import Missing, Undefined
from pybotx.models.message.markup import (
    BubbleMarkup,
    ButtonTextAlign,
    KeyboardMarkup,
)

TMarkup = TypeVar("TMarkup", BubbleMarkup, KeyboardMarkup)


@dataclass(slots=True)
class MessageMarkup:
    bubbles: BubbleMarkup = field(default_factory=BubbleMarkup)
    keyboard: KeyboardMarkup = field(default_factory=KeyboardMarkup)

    def add_bubble(
        self,
        *,
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
        self.bubbles.add_button(
            label=label,
            command=command,
            data=data,
            text_color=text_color,
            background_color=background_color,
            align=align,
            silent=silent,
            width_ratio=width_ratio,
            alert=alert,
            process_on_client=process_on_client,
            link=link,
            new_row=new_row,
        )

    def add_keyboard(
        self,
        *,
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
        self.keyboard.add_button(
            label=label,
            command=command,
            data=data,
            text_color=text_color,
            background_color=background_color,
            align=align,
            silent=silent,
            width_ratio=width_ratio,
            alert=alert,
            process_on_client=process_on_client,
            link=link,
            new_row=new_row,
        )


def clone_markup(markup: TMarkup) -> TMarkup:
    cloned_markup = type(markup)()
    for row in markup:
        cloned_markup.add_row([deepcopy(button) for button in row])
    return cloned_markup


def merge_message_markup(
    primary: MessageMarkup,
    additional: MessageMarkup,
) -> MessageMarkup:
    merged_bubbles = clone_markup(primary.bubbles)
    for row in additional.bubbles:
        merged_bubbles.add_row([deepcopy(button) for button in row])

    merged_keyboard = clone_markup(primary.keyboard)
    for row in additional.keyboard:
        merged_keyboard.add_row([deepcopy(button) for button in row])

    return MessageMarkup(bubbles=merged_bubbles, keyboard=merged_keyboard)
