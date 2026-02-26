from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.messages_pager import MessagesPagerWidget
from pybotx.widgets.pagination import MESSAGE_IDS_KEY


def _build_bot_mock() -> SimpleNamespace:
    return SimpleNamespace(
        send=AsyncMock(
            side_effect=[
                uuid4(),
                uuid4(),
                uuid4(),
            ]
        ),
        edit_message=AsyncMock(),
    )


@pytest.mark.asyncio
async def test__messages_pager_widget__display(
    incoming_message_factory: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pybotx.widgets.pagination.asyncio.sleep", AsyncMock())

    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = MessagesPagerWidget(
        elements=["1", "2", "3"],
        page_size=2,
        message=message,
        bot=bot,
        command="/widget",
    )
    await widget.display()

    last_sent_message = bot.send.await_args_list[-1].kwargs["message"]
    assert last_sent_message.body == "Element: 2"
    assert MESSAGE_IDS_KEY in last_sent_message.metadata


@pytest.mark.asyncio
async def test__messages_pager_widget__display_custom_template(
    incoming_message_factory: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pybotx.widgets.pagination.asyncio.sleep", AsyncMock())

    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = MessagesPagerWidget(
        elements=["x"],
        page_size=1,
        item_template="Elem #{index}/{total}: {element}",
        message=message,
        bot=bot,
        command="/widget",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    assert sent_message.body == "Elem #1/1: x"
