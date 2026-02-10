import json
from typing import Any, Literal, cast

from pydantic import RootModel
from pydantic_core import to_jsonable_python

from pybotx.infrastructure.contracts.api_base import (
    UnverifiedPayloadBaseModel,
    _remove_undefined,
)
from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.message.markup import (
    Button,
    ButtonTextAlign,
    Markup,
)


class BotXAPIButtonOptions(UnverifiedPayloadBaseModel):
    silent: Missing[bool]
    font_color: Missing[str]
    background_color: Missing[str]
    align: Missing[str]
    h_size: Missing[int]
    show_alert: Missing[Literal[True]]
    alert_text: Missing[str]
    handler: Missing[Literal["client"]]
    link: Missing[str]


class BotXAPIButton(UnverifiedPayloadBaseModel):
    command: str
    label: str
    data: dict[str, Any]
    opts: BotXAPIButtonOptions


class BotXAPIMarkup(RootModel[list[list[BotXAPIButton]]]):
    def json(self) -> str:  # type: ignore[override]
        clean_dict = _remove_undefined(self.model_dump())
        return json.dumps(clean_dict, default=to_jsonable_python, ensure_ascii=False)

    def jsonable_dict(self) -> list[list[dict[str, Any]]]:
        return cast(list[list[dict[str, Any]]], json.loads(self.json()))


def api_button_from_domain(button: Button) -> BotXAPIButton:
    show_alert: Missing[Literal[True]] = Undefined
    if button.alert is not Undefined:
        show_alert = True

    handler: Missing[Literal["client"]] = Undefined
    if button.process_on_client:
        handler = "client"

    if button.link is not Undefined:
        handler = "client"

    return BotXAPIButton(
        command=button.command,
        label=button.label,
        data=button.data,
        opts=BotXAPIButtonOptions(
            silent=button.silent,
            font_color=button.text_color,
            background_color=button.background_color,
            align=button.align,
            h_size=button.width_ratio,
            alert_text=button.alert,
            show_alert=show_alert,
            handler=handler,
            link=button.link,
        ),
    )


def api_markup_from_domain(markup: Markup) -> BotXAPIMarkup:
    return BotXAPIMarkup(
        root=[
            [api_button_from_domain(button) for button in buttons] for buttons in markup
        ]
    )
