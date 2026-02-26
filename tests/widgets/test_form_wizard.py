from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from pybotx.widgets.form_wizard import (
    FORM_ACTION_BACK,
    FORM_ACTION_CANCEL,
    FORM_ACTION_KEY,
    FORM_ACTION_NEXT,
    FORM_ACTION_RESET,
    FORM_INPUT_KEY,
    FORM_STEP_INDEX_KEY,
    FORM_VALUES_KEY,
    FormWizardStep,
    FormWizardWidget,
)


def _build_bot_mock() -> SimpleNamespace:
    return SimpleNamespace(send=AsyncMock(return_value=uuid4()), edit_message=AsyncMock())


def _steps() -> list[FormWizardStep]:
    return [
        FormWizardStep(field="name", label="Введите имя"),
        FormWizardStep(field="email", label="Введите email"),
    ]


@pytest.mark.asyncio
async def test__form_wizard_widget__active_step(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory(body="/form John")
    bot = _build_bot_mock()

    widget = FormWizardWidget(
        steps=_steps(),
        label="Форма",
        message=message,
        bot=bot,
        command="/form",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    assert "Шаг 1/2" in sent_message.body
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["Далее", "Отмена", "Использовать текст сообщения"]
    assert widget.is_active


@pytest.mark.asyncio
async def test__form_wizard_widget__next_and_back(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.metadata = {
        FORM_STEP_INDEX_KEY: 1,
        FORM_VALUES_KEY: {"name": "Alice"},
    }
    message.data = {FORM_ACTION_KEY: FORM_ACTION_BACK}
    bot = _build_bot_mock()

    widget = FormWizardWidget(
        steps=_steps(),
        label="Форма",
        message=message,
        bot=bot,
        command="/form",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert "Шаг 1/2" in sent_message.body

    message.data = {}
    message.metadata = {
        FORM_STEP_INDEX_KEY: "1",
        FORM_VALUES_KEY: {"name": "Alice"},
    }
    widget = FormWizardWidget(
        steps=_steps(),
        label="Форма",
        message=message,
        bot=bot,
        command="/form",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["Назад", "Далее", "Отмена", "Использовать текст сообщения"]

    message.data = {
        FORM_ACTION_KEY: FORM_ACTION_NEXT,
        FORM_INPUT_KEY: "alice@example.com",
    }
    message.metadata = {
        FORM_STEP_INDEX_KEY: 1,
        FORM_VALUES_KEY: {"name": "Alice"},
    }
    widget = FormWizardWidget(
        steps=_steps(),
        label="Форма",
        message=message,
        bot=bot,
        command="/form",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert "Форма заполнена." in sent_message.body
    assert sent_message.metadata[FORM_VALUES_KEY]["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test__form_wizard_widget__cancel_and_reset(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.data = {FORM_ACTION_KEY: FORM_ACTION_CANCEL}
    bot = _build_bot_mock()

    widget = FormWizardWidget(
        steps=_steps(),
        label="Форма",
        message=message,
        bot=bot,
        command="/form",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert "Операция отменена." in sent_message.body

    message.data = {FORM_ACTION_KEY: FORM_ACTION_RESET}
    message.metadata = {
        FORM_VALUES_KEY: {"name": "Bob"},
        FORM_STEP_INDEX_KEY: 1,
    }
    widget = FormWizardWidget(
        steps=_steps(),
        label="Форма",
        message=message,
        bot=bot,
        command="/form",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert "Шаг 1/2" in sent_message.body
    assert sent_message.metadata[FORM_VALUES_KEY] == {}


def test__form_wizard_widget__get_values(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.metadata = {FORM_VALUES_KEY: {"a": 1}}
    assert FormWizardWidget.get_values(message) == {"a": 1}

    message.metadata = {FORM_VALUES_KEY: "bad"}
    with pytest.raises(RuntimeError):
        FormWizardWidget.get_values(message)


@pytest.mark.asyncio
async def test__form_wizard_widget__input_ignored_for_completed_step(
    incoming_message_factory: object,
) -> None:
    message = incoming_message_factory()
    message.metadata = {
        FORM_STEP_INDEX_KEY: 2,
        FORM_VALUES_KEY: {"name": "Alice"},
    }
    message.data = {FORM_INPUT_KEY: "should-not-be-used"}
    bot = _build_bot_mock()

    widget = FormWizardWidget(
        steps=_steps(),
        label="Форма",
        message=message,
        bot=bot,
        command="/form",
    )
    await widget.display()
    sent_message = bot.send.await_args.kwargs["message"]
    assert "Форма заполнена." in sent_message.body
    assert sent_message.metadata[FORM_VALUES_KEY] == {"name": "Alice"}
