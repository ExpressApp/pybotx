import json
from typing import Dict, Any, List


from pybotx.models.message.markup import (
    BotXAPIMarkup,
    BotXAPIButton,
    BotXAPIButtonOptions,
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
    expected_dict: List[List[Dict[str, Any]]] = [
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
