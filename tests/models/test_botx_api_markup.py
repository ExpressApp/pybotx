import json
import warnings
from typing import Any


from pybotx import BubbleMarkup
from pybotx.models.message.markup import (
    BotXAPIMarkup,
    BotXAPIButton,
    BotXAPIButtonOptions,
    api_markup_from_domain,
)


def test_botx_api_markup_json() -> None:
    # - Arrange -
    markup = BotXAPIMarkup(
        root=[
            [
                BotXAPIButton(
                    command="/test",
                    label="Test",
                    data={},
                    opts=BotXAPIButtonOptions(
                        silent=True,
                        font_color=None,
                        background_color=None,
                        align="center",
                        h_size=None,
                        show_alert=None,
                        alert_text=None,
                        handler=None,
                        link=None,
                    ),
                )
            ]
        ]
    )

    # - Act -
    json_str = markup.json()

    # - Assert -
    expected_json = json.dumps(
        [
            [
                {
                    "command": "/test",
                    "label": "Test",
                    "data": {},
                    "opts": {
                        "silent": True,
                        "font_color": None,
                        "background_color": None,
                        "align": "center",
                        "h_size": None,
                        "show_alert": None,
                        "alert_text": None,
                        "handler": None,
                        "link": None,
                    },
                }
            ]
        ],
        ensure_ascii=False,
    )
    assert json_str == expected_json


def test_botx_api_markup_jsonable_dict() -> None:
    # - Arrange -
    markup = BotXAPIMarkup(
        root=[
            [
                BotXAPIButton(
                    command="/test",
                    label="Test",
                    data={},
                    opts=BotXAPIButtonOptions(
                        silent=True,
                        font_color=None,
                        background_color=None,
                        align="center",
                        h_size=None,
                        show_alert=None,
                        alert_text=None,
                        handler=None,
                        link=None,
                    ),
                )
            ]
        ]
    )

    # - Act -
    jsonable_dict = markup.jsonable_dict()

    # - Assert -
    expected_dict: list[list[dict[str, Any]]] = [
        [
            {
                "command": "/test",
                "label": "Test",
                "data": {},
                "opts": {
                    "silent": True,
                    "font_color": None,
                    "background_color": None,
                    "align": "center",
                    "h_size": None,
                    "show_alert": None,
                    "alert_text": None,
                    "handler": None,
                    "link": None,
                },
            }
        ]
    ]
    assert jsonable_dict == expected_dict


def test_botx_api_markup_link_button_without_command() -> None:
    # - Arrange -
    markup = BubbleMarkup()
    markup.add_button(
        label="Open me",
        link="https://example.com",
    )

    # - Act -
    with warnings.catch_warnings(record=True) as captured_warnings:
        warnings.simplefilter("always")
        jsonable_dict = api_markup_from_domain(markup).jsonable_dict()

    # - Assert -
    expected_dict: list[list[dict[str, Any]]] = [
        [
            {
                "label": "Open me",
                "data": {},
                "opts": {
                    "silent": True,
                    "align": "center",
                    "handler": "client",
                    "link": "https://example.com",
                },
            }
        ]
    ]
    assert jsonable_dict == expected_dict
    assert not captured_warnings
