from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Literal, Optional, Union

from botx.missing import Missing, Undefined
from botx.models.api_base import UnverifiedPayloadBaseModel


@dataclass
class Button:
    command: str
    label: str
    data: Dict[str, Any] = field(default_factory=dict)

    silent: bool = True  # BotX has `False` as default, so Missing type can't be used
    width_ratio: Missing[int] = Undefined
    alert: Missing[str] = Undefined
    process_on_client: Missing[bool] = Undefined


ButtonRow = List[Button]


class BaseMarkup:
    def __init__(self, buttons: Optional[List[ButtonRow]] = None) -> None:
        self._buttons = buttons or []

    def __iter__(self) -> Iterator[ButtonRow]:
        return iter(self._buttons)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseMarkup):
            raise NotImplementedError

        # https://github.com/wemake-services/wemake-python-styleguide/issues/2172
        return self._buttons == other._buttons  # noqa: WPS437

    def add_built_button(self, button: Button, new_row: bool = True) -> None:
        if new_row:
            self._buttons.append([button])
            return

        if not self._buttons:
            self._buttons.append([])

        self._buttons[-1].append(button)

    def add_button(
        self,
        command: str,
        label: str,
        data: Optional[Dict[str, Any]] = None,
        silent: bool = True,
        width_ratio: Missing[int] = Undefined,
        alert: Missing[str] = Undefined,
        process_on_client: Missing[bool] = Undefined,
        new_row: bool = True,
    ) -> None:
        button = Button(
            command=command,
            label=label,
            data=data or {},
            silent=silent,
            width_ratio=width_ratio,
            alert=alert,
            process_on_client=process_on_client,
        )
        self.add_built_button(button, new_row=new_row)

    def add_row(self, button_row: ButtonRow) -> None:
        self._buttons.append(button_row)


class BubbleMarkup(BaseMarkup):
    """Class for managing inline message buttons."""


class KeyboardMarkup(BaseMarkup):
    """Class for managing keyboard message buttons."""


Markup = Union[BubbleMarkup, KeyboardMarkup]


class BotXAPIButtonOptions(UnverifiedPayloadBaseModel):
    silent: Missing[bool]
    h_size: Missing[int]
    show_alert: Missing[Literal[True]]
    alert_text: Missing[str]
    handler: Missing[Literal["client"]]


class BotXAPIButton(UnverifiedPayloadBaseModel):
    command: str
    label: str
    data: Dict[str, Any]
    opts: BotXAPIButtonOptions


class BotXAPIMarkup(UnverifiedPayloadBaseModel):
    __root__: List[List[BotXAPIButton]]


def api_button_from_domain(button: Button) -> BotXAPIButton:
    show_alert: Missing[Literal[True]] = Undefined
    if button.alert is not Undefined:
        show_alert = True

    handler: Missing[Literal["client"]] = Undefined
    if button.process_on_client:
        handler = "client"

    return BotXAPIButton(
        command=button.command,
        label=button.label,
        data=button.data,
        opts=BotXAPIButtonOptions(
            silent=button.silent,
            h_size=button.width_ratio,
            alert_text=button.alert,
            show_alert=show_alert,
            handler=handler,
        ),
    )


def api_markup_from_domain(markup: Markup) -> BotXAPIMarkup:
    return BotXAPIMarkup(
        __root__=[
            [api_button_from_domain(button) for button in buttons] for buttons in markup
        ],
    )
