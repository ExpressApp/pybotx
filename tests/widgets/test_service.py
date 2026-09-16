from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.base import PYBOTX_WIDGET_FLAG
from pybotx.widgets.markup import MessageMarkup
from pybotx.widgets.service import send_or_update_message


def _build_bot_mock() -> Any:
    return SimpleNamespace(
        send=AsyncMock(return_value=uuid4()),
        edit_message=AsyncMock(),
    )


@pytest.mark.asyncio
async def test__send_or_update_message__send(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()
    markup = MessageMarkup()
    markup.add_bubble(command="/send", label="Send")

    await send_or_update_message(message, bot, body="body", markup=markup)

    assert bot.send.await_count == 1
    assert bot.edit_message.await_count == 0


@pytest.mark.asyncio
async def test__send_or_update_message__update(
    incoming_message_factory: Any,
) -> None:
    message = incoming_message_factory()
    message.source_sync_id = uuid4()
    message.metadata[PYBOTX_WIDGET_FLAG] = 1
    bot = _build_bot_mock()

    await send_or_update_message(message, bot, body="body")

    assert bot.send.await_count == 0
    assert bot.edit_message.await_count == 1
