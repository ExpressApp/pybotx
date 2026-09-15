from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.checktable import CheckboxContent, ChecktableWidget
from pybotx.widgets.undefined import undefined


def _build_bot_mock() -> Any:
    return SimpleNamespace(
        send=AsyncMock(return_value=uuid4()),
        edit_message=AsyncMock(),
    )


def test__checkbox_content__validation_error() -> None:
    with pytest.raises(ValueError):
        CheckboxContent[str](
            label="Field",
            command="/command",
            checkbox_value="unknown",
            mapping={"known": "Known"},
        )


@pytest.mark.asyncio
async def test__checktable_widget__display(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    checkboxes: list[CheckboxContent[Any]] = [
        CheckboxContent[str](
            label="Undefined",
            command="/fill",
            checkbox_value=undefined,
        ),
        CheckboxContent[str](
            label="None",
            command="/fill",
            checkbox_value=None,
        ),
        CheckboxContent[str](
            label="Mapped",
            command="/select",
            checkbox_value="k1",
            mapping={"k1": "Value 1"},
        ),
        CheckboxContent[str](
            label="Mapped undefined",
            command="/select",
            checkbox_value=undefined,
            mapping={"k1": "Value 1"},
        ),
        CheckboxContent[int](
            label="Numeric",
            command="/fill",
            checkbox_value=7,
        ),
    ]

    widget = ChecktableWidget(
        checkboxes=checkboxes,
        label="Checktable",
        uncheck_command="/uncheck",
        message=message,
        bot=bot,
        command="/checktable",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    rows = [[button.label for button in row] for row in sent_message.bubbles]

    assert sent_message.body == "Checktable"
    assert rows == [
        ["☐ Undefined", "Ввести"],
        ["☑ None", "[Пусто]"],
        ["☑ Mapped", "Value 1"],
        ["☐ Mapped undefined", "Выбрать"],
        ["☑ Numeric", "7"],
    ]
