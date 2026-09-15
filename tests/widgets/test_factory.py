from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import date

import pytest

from pybotx.widgets import (
    WidgetContext,
    WidgetDefaults,
    WidgetFactory,
)
from pybotx.widgets.async_job import ASYNC_JOB_FAILED, ASYNC_JOB_QUEUED
from pybotx.widgets.base import WIDGET_RESULT_MODE_MESSAGE
from pybotx.widgets.checklist import CHECKED_ITEMS_KEY, SELECTED_ITEM_KEY
from pybotx.widgets.checktable import CheckboxContent
from pybotx.widgets.date_range import DATE_RANGE_CURSOR_KEY
from pybotx.widgets.file_batch import (
    FILE_BATCH_FILES_KEY,
    FILE_BATCH_PAGE_KEY,
    BatchFileItem,
)
from pybotx.widgets.pagination import MESSAGE_IDS_KEY
from pybotx.widgets.form_wizard import FORM_VALUES_KEY, FormWizardStep
from pybotx.widgets.markup import MessageMarkup
from pybotx.widgets.messages_pager import MessagesPagerWidget
from pybotx.widgets.multi_select import MULTI_SELECTED_VALUES_KEY, MULTI_SELECT_VALUE_KEY
from pybotx.widgets.range import ELEMENTS_KEY
from pybotx.widgets.search_select import SEARCH_PAGE_KEY, SEARCH_QUERY_KEY
from pybotx.widgets.select import SelectOption
from pybotx.widgets.table import TABLE_PAGE_KEY, TABLE_QUERY_KEY
from pybotx.widgets.undefined import undefined


def _build_bot_mock() -> Any:
    return SimpleNamespace(
        send=AsyncMock(return_value=uuid4()),
        edit_message=AsyncMock(),
        answer_message=AsyncMock(return_value=uuid4()),
    )


def test__widget_context__exports_base_widget_kwargs(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    markup = MessageMarkup()
    context = WidgetContext(
        message=message,
        bot=bot,
        command="/confirm",
        additional_markup=markup,
        result_mode=WIDGET_RESULT_MODE_MESSAGE,
    )

    assert context.as_widget_kwargs() == {
        "message": message,
        "bot": bot,
        "command": "/confirm",
        "additional_markup": markup,
        "result_mode": WIDGET_RESULT_MODE_MESSAGE,
    }


@pytest.mark.asyncio
async def test__widget_factory__builds_confirm_widget_with_defaults(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/confirm",
        ),
    )

    widget = factory.confirm(label="Подтвердить действие")
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    rows = [[button.label for button in row] for row in sent_message.bubbles]
    assert rows == [["Подтвердить", "Отмена"]]


@pytest.mark.asyncio
async def test__widget_factory__applies_custom_defaults_to_approval_widget(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    defaults = WidgetDefaults(
        approve_label="Approve",
        reject_label="Reject",
        comment_label="Comment",
    )
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/approval",
        ),
        defaults=defaults,
    )

    widget = factory.approval(label="Review request")
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    rows = [[button.label for button in row] for row in sent_message.bubbles]
    assert rows == [["Approve", "Reject"], ["Comment"]]


@pytest.mark.asyncio
async def test__widget_factory__select_supports_context_and_per_call_overrides(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    message.data = {"select_value": "b"}
    bot = _build_bot_mock()
    context_markup = MessageMarkup()
    context_markup.add_keyboard(command="/ctx", label="Context keyboard")
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/select",
            additional_markup=context_markup,
        ),
    )

    widget = factory.select(
        options=[
            "a",
            SelectOption(value="b", label="Bee"),
        ],
        label="Выберите",
        selected_prefix="> ",
        result_mode=WIDGET_RESULT_MODE_MESSAGE,
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    bubble_rows = [[button.label for button in row] for row in sent_message.bubbles]
    keyboard_rows = [[button.label for button in row] for row in sent_message.keyboard]
    assert bubble_rows == [["a"], ["> Bee"]]
    assert keyboard_rows == [["Context keyboard"]]
    assert widget.result_mode == WIDGET_RESULT_MODE_MESSAGE


@pytest.mark.asyncio
async def test__widget_factory__search_select_uses_defaults_and_context(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    message.data = {SEARCH_QUERY_KEY: "ap", SEARCH_PAGE_KEY: 1}
    bot = _build_bot_mock()
    defaults = WidgetDefaults(
        selected_prefix="> ",
        search_empty_label="Empty",
    )
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/search",
        ),
        defaults=defaults,
    )

    widget = factory.search_select(
        options=["apple", "banana", "apricot"],
        label="Поиск",
        page_size=1,
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["apricot", "Назад"]
    assert sent_message.body == "Поиск\nПоиск: ap"


@pytest.mark.asyncio
async def test__widget_factory__multi_select_supports_context_and_overrides(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    message.metadata = {MULTI_SELECTED_VALUES_KEY: ["a"]}
    message.data = {MULTI_SELECT_VALUE_KEY: "b"}
    bot = _build_bot_mock()
    context_markup = MessageMarkup()
    context_markup.add_keyboard(command="/ctx", label="Done")
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/multi",
            additional_markup=context_markup,
            result_mode=WIDGET_RESULT_MODE_MESSAGE,
        ),
    )

    widget = factory.multi_select(
        options=["a", "b", "c"],
        label="Выберите",
        max_selected=3,
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    bubble_rows = [[button.label for button in row] for row in sent_message.bubbles]
    keyboard_rows = [[button.label for button in row] for row in sent_message.keyboard]
    assert sent_message.metadata[MULTI_SELECTED_VALUES_KEY] == ["a", "b"]
    assert bubble_rows == [["☑ a"], ["☑ b"], ["☐ c"]]
    assert keyboard_rows == [["Done"]]
    assert widget.result_mode == WIDGET_RESULT_MODE_MESSAGE


@pytest.mark.asyncio
async def test__widget_factory__form_wizard_uses_context_and_result_mode(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)(body="/form Alice")
    message.metadata = {FORM_VALUES_KEY: {"name": "Alice"}}
    bot = _build_bot_mock()
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/form",
            result_mode=WIDGET_RESULT_MODE_MESSAGE,
        ),
    )

    widget = factory.form_wizard(
        steps=[
            FormWizardStep(field="name", label="Введите имя"),
            FormWizardStep(field="email", label="Введите email"),
        ],
        label="Форма",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert "Шаг 1/2" in sent_message.body
    assert labels == ["Далее", "Отмена", "Использовать текст сообщения"]
    assert widget.result_mode == WIDGET_RESULT_MODE_MESSAGE


@pytest.mark.asyncio
async def test__widget_factory__table_supports_defaults_and_context(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    message.data = {
        TABLE_QUERY_KEY: "a",
        TABLE_PAGE_KEY: 0,
    }
    bot = _build_bot_mock()
    context_markup = MessageMarkup()
    context_markup.add_keyboard(command="/ctx", label="Refresh")
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/table",
            additional_markup=context_markup,
        ),
    )

    widget = factory.table(
        rows=[
            {"name": "Alice", "role": "admin"},
            {"name": "Charlie", "role": "analyst"},
        ],
        columns=["name", "role"],
        label="Пользователи",
        page_size=1,
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    keyboard_rows = [[button.label for button in row] for row in sent_message.keyboard]
    assert "Пользователи" in sent_message.body
    assert "Фильтр: a" in sent_message.body
    assert labels == ["Вперед", "Сорт: name", "Сорт: role", "Сбросить фильтр"]
    assert keyboard_rows == [["Refresh"]]


@pytest.mark.asyncio
async def test__widget_factory__calendar_supports_context_and_overrides(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/calendar",
        ),
    )

    widget = factory.calendar(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        include_past=True,
        result_mode=WIDGET_RESULT_MODE_MESSAGE,
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert sent_message.body == "Выберите дату"
    assert "Пн" in labels
    assert any(month in labels for month in widget.MONTHS.values())
    assert widget.result_mode == WIDGET_RESULT_MODE_MESSAGE


@pytest.mark.asyncio
async def test__widget_factory__range_supports_context_and_markup(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    context_markup = MessageMarkup()
    context_markup.add_keyboard(command="/ctx", label="Close")
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/range",
            additional_markup=context_markup,
        ),
    )

    widget = factory.range(
        elements=["one", "two", "three"],
        label_template="Item: {element}",
        forward_label="Next",
        backward_label="Prev",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    rows = [[button.label for button in row] for row in sent_message.bubbles]
    keyboard_rows = [[button.label for button in row] for row in sent_message.keyboard]
    assert sent_message.body == "Item: one"
    assert sent_message.metadata[ELEMENTS_KEY] == ["one", "two", "three"]
    assert rows == [["Next"]]
    assert keyboard_rows == [["Close"]]


@pytest.mark.asyncio
async def test__widget_factory__carousel_supports_context_and_result_mode(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    context_markup = MessageMarkup()
    context_markup.add_keyboard(command="/ctx", label="Close")
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/carousel",
            additional_markup=context_markup,
            result_mode=WIDGET_RESULT_MODE_MESSAGE,
        ),
    )

    widget = factory.carousel(
        widget_content=["a", "b", "c", "d"],
        label="Carousel",
        displayed_content_count=2,
        loop=False,
        inline=True,
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    keyboard_rows = [[button.label for button in row] for row in sent_message.keyboard]
    assert labels == ["a", "b", "➡️"]
    assert keyboard_rows == [["Close"]]
    assert widget.result_mode == WIDGET_RESULT_MODE_MESSAGE


@pytest.mark.asyncio
async def test__widget_factory__pagination_supports_context_and_markup(
    incoming_message_factory: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pybotx.widgets.pagination.asyncio.sleep", AsyncMock())

    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    context_markup = MessageMarkup()
    context_markup.add_keyboard(command="/ctx", label="Close")
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/pagination",
            additional_markup=context_markup,
        ),
    )

    widget = factory.pagination(
        widget_content=["1", "2", "3"],
        paginate_by=2,
        delay_between_messages=0.0,
    )
    await widget.display()

    assert bot.send.await_count == 2
    last_message = bot.send.await_args_list[-1].kwargs["message"]
    bubble_rows = [[button.label for button in row] for row in last_message.bubbles]
    keyboard_rows = [[button.label for button in row] for row in last_message.keyboard]
    assert last_message.body == "2"
    assert bubble_rows == [["➡️ Вперёд к [3]"]]
    assert keyboard_rows == [["Close"]]
    assert MESSAGE_IDS_KEY in last_message.metadata


@pytest.mark.asyncio
async def test__widget_factory__messages_pager_supports_context_and_template(
    incoming_message_factory: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pybotx.widgets.pagination.asyncio.sleep", AsyncMock())

    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    context_markup = MessageMarkup()
    context_markup.add_keyboard(command="/ctx", label="Close")
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/pager",
            additional_markup=context_markup,
        ),
    )

    widget = factory.messages_pager(
        elements=["x", "y", "z"],
        page_size=2,
        item_template="Elem #{index}/{total}: {element}",
        delay_between_messages=0.0,
    )

    assert isinstance(widget, MessagesPagerWidget)
    await widget.display()

    last_message = bot.send.await_args_list[-1].kwargs["message"]
    keyboard_rows = [[button.label for button in row] for row in last_message.keyboard]
    assert last_message.body == "Elem #2/3: y"
    assert keyboard_rows == [["Close"]]
    assert MESSAGE_IDS_KEY in last_message.metadata


@pytest.mark.asyncio
async def test__widget_factory__date_range_supports_context_and_result_mode(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/date-range",
            result_mode=WIDGET_RESULT_MODE_MESSAGE,
        ),
    )

    widget = factory.date_range(label="Период")
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert "Период" in sent_message.body
    assert labels == ["Сегодня", "Завтра"]
    assert sent_message.metadata[DATE_RANGE_CURSOR_KEY] == "start"
    assert widget.result_mode == WIDGET_RESULT_MODE_MESSAGE


@pytest.mark.asyncio
async def test__widget_factory__async_job_supports_context_and_markup(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    context_markup = MessageMarkup()
    context_markup.add_keyboard(command="/ctx", label="Close")
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/job",
            additional_markup=context_markup,
        ),
    )

    widget = factory.async_job(
        job_id="job-1",
        status=ASYNC_JOB_QUEUED,
        details="Подготовка",
        result_mode=WIDGET_RESULT_MODE_MESSAGE,
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    keyboard_rows = [[button.label for button in row] for row in sent_message.keyboard]
    assert "Задача job-1" in sent_message.body
    assert labels == ["Обновить", "Отменить"]
    assert keyboard_rows == [["Close"]]
    assert widget.result_mode == WIDGET_RESULT_MODE_MESSAGE


@pytest.mark.asyncio
async def test__widget_factory__async_job_failed_state_is_preserved(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/job",
        ),
    )

    widget = factory.async_job(
        job_id="job-2",
        status=ASYNC_JOB_FAILED,
        details="Ошибка",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    assert labels == ["Повторить", "Обновить"]


@pytest.mark.asyncio
async def test__widget_factory__file_batch_supports_context_and_markup(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    message.data = {FILE_BATCH_PAGE_KEY: 0}
    bot = _build_bot_mock()
    context_markup = MessageMarkup()
    context_markup.add_keyboard(command="/ctx", label="Close")
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/batch",
            additional_markup=context_markup,
            result_mode=WIDGET_RESULT_MODE_MESSAGE,
        ),
    )

    widget = factory.file_batch(
        files=[
            BatchFileItem(name="a.txt", status="done"),
            {"name": "b.txt", "status": "failed", "error": "oops"},
            "c.txt",
        ],
        page_size=2,
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    labels = [button.label for row in sent_message.bubbles for button in row]
    keyboard_rows = [[button.label for button in row] for row in sent_message.keyboard]
    assert "Всего: 3" in sent_message.body
    assert labels == ["a.txt", "b.txt", "Вперед", "Повторить ошибки"]
    assert keyboard_rows == [["Close"]]
    assert FILE_BATCH_FILES_KEY in sent_message.metadata
    assert widget.result_mode == WIDGET_RESULT_MODE_MESSAGE


@pytest.mark.asyncio
async def test__widget_factory__checklist_supports_context_and_checked_items(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    message.metadata = {CHECKED_ITEMS_KEY: ["b"]}
    message.data = {SELECTED_ITEM_KEY: "a"}
    bot = _build_bot_mock()
    context_markup = MessageMarkup()
    context_markup.add_keyboard(command="/ctx", label="Close")
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/checklist",
            additional_markup=context_markup,
        ),
    )

    widget = factory.checklist(
        widget_content=["a", ["b", "c"]],
        label="Checklist",
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    rows = [[button.label for button in row] for row in sent_message.bubbles]
    keyboard_rows = [[button.label for button in row] for row in sent_message.keyboard]
    assert sent_message.metadata[CHECKED_ITEMS_KEY] == ["b", "a"]
    assert rows == [["☑ a"], ["☑ b", "☐ c"]]
    assert keyboard_rows == [["Close"]]


@pytest.mark.asyncio
async def test__widget_factory__checktable_supports_context_and_markup(
    incoming_message_factory: object,
) -> None:
    message = cast(Any, incoming_message_factory)()
    bot = _build_bot_mock()
    context_markup = MessageMarkup()
    context_markup.add_keyboard(command="/ctx", label="Close")
    factory = WidgetFactory(
        context=WidgetContext(
            message=message,
            bot=bot,
            command="/checktable",
            additional_markup=context_markup,
        ),
    )

    widget = factory.checktable(
        checkboxes=[
            CheckboxContent[str](
                label="Undefined",
                command="/fill",
                checkbox_value=undefined,
            ),
            CheckboxContent[str](
                label="Mapped",
                command="/select",
                checkbox_value="k1",
                mapping={"k1": "Value 1"},
            ),
        ],
        label="Checktable",
        uncheck_command="/uncheck",
        result_mode=WIDGET_RESULT_MODE_MESSAGE,
    )
    await widget.display()

    sent_message = bot.send.await_args.kwargs["message"]
    rows = [[button.label for button in row] for row in sent_message.bubbles]
    keyboard_rows = [[button.label for button in row] for row in sent_message.keyboard]
    assert rows == [["☐ Undefined", "Ввести"], ["☑ Mapped", "Value 1"]]
    assert keyboard_rows == [["Close"]]
    assert widget.result_mode == WIDGET_RESULT_MODE_MESSAGE
