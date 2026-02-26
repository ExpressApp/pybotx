from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.async_job import (
    ASYNC_JOB_ACTION_KEY,
    ASYNC_JOB_ACTION_REFRESH,
    ASYNC_JOB_ACTION_RETRY,
    ASYNC_JOB_FAILED,
    ASYNC_JOB_QUEUED,
    ASYNC_JOB_STATUS_KEY,
    AsyncJobWidget,
)


def _build_bot_mock() -> SimpleNamespace:
    return SimpleNamespace(send=AsyncMock(return_value=uuid4()), edit_message=AsyncMock())


@pytest.mark.asyncio
async def test__async_job_widget__queued(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = AsyncJobWidget(
        job_id="job-1",
        status=ASYNC_JOB_QUEUED,
        message=message,
        bot=bot,
        command="/job",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["Обновить", "Отменить"]


@pytest.mark.asyncio
async def test__async_job_widget__failed_and_done(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    bot = _build_bot_mock()

    widget = AsyncJobWidget(
        job_id="job-2",
        status=ASYNC_JOB_FAILED,
        details="Ошибка",
        message=message,
        bot=bot,
        command="/job",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert "Ошибка" in sent_message.body
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["Повторить", "Обновить"]

    widget = AsyncJobWidget(
        job_id="job-3",
        status="done",
        message=message,
        bot=bot,
        command="/job",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["Обновить"]


def test__async_job_widget__getters(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.data = {ASYNC_JOB_ACTION_KEY: ASYNC_JOB_ACTION_REFRESH}
    assert AsyncJobWidget.get_action(message) == ASYNC_JOB_ACTION_REFRESH

    message.data = {ASYNC_JOB_ACTION_KEY: ASYNC_JOB_ACTION_RETRY}
    assert AsyncJobWidget.get_action(message) == ASYNC_JOB_ACTION_RETRY

    message.data = {}
    with pytest.raises(RuntimeError):
        AsyncJobWidget.get_action(message)

    message.metadata = {ASYNC_JOB_STATUS_KEY: "done"}
    assert AsyncJobWidget.get_status(message) == "done"

    message.metadata = {}
    with pytest.raises(RuntimeError):
        AsyncJobWidget.get_status(message)
