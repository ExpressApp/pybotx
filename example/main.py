import os
from http import HTTPStatus
from typing import Final
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pybotx import (
    Bot,
    BotAccountWithSecret,
    BubbleMarkup,
    HandlerCollector,
    IncomingMessage,
    OutgoingMessage,
    build_command_accepted_response,
)
from pybotx.widgets import (
    ApprovalWidget,
    AsyncJobWidget,
    BatchFileItem,
    CalendarWidget,
    CarouselWidget,
    CheckListWidget,
    CheckboxContent,
    ChecktableWidget,
    ConfirmWidget,
    DateRangeWidget,
    FileBatchWidget,
    FormWizardStep,
    FormWizardWidget,
    MessageMarkup,
    MessagesPagerWidget,
    MultiSelectWidget,
    PaginationWidget,
    RangeWidget,
    RunnerHookResult,
    SearchSelectWidget,
    SelectOption,
    SelectWidget,
    TableWidget,
    on_action,
    on_completed,
    on_data_key,
    widget_command,
    undefined,
)
from pybotx.widgets.async_job import (
    ASYNC_JOB_ACTION_CANCEL,
    ASYNC_JOB_ACTION_KEY,
    ASYNC_JOB_ACTION_REFRESH,
    ASYNC_JOB_ACTION_RETRY,
    ASYNC_JOB_CANCELLED,
    ASYNC_JOB_DONE,
    ASYNC_JOB_FAILED,
    ASYNC_JOB_ID_KEY,
    ASYNC_JOB_QUEUED,
    ASYNC_JOB_RUNNING,
    ASYNC_JOB_STATUS_KEY,
)
from pybotx.widgets.confirm import (
    CANCEL_ACTION,
    CONFIRM_ACTION,
)
from pybotx.widgets.file_batch import (
    FILE_BATCH_ACTION_ITEM,
    FILE_BATCH_ACTION_RETRY_FAILED,
    FILE_BATCH_FILES_KEY,
)
from pybotx.widgets.calendar import SELECTED_DATE_KEY as CALENDAR_SELECTED_DATE_KEY
from pybotx.widgets.carousel import SELECTED_VALUE_KEY as CAROUSEL_SELECTED_VALUE_KEY
from pybotx.widgets.range import CURRENT_INDEX_KEY
from pybotx.widgets.select import SELECT_VALUE_KEY
from pybotx.widgets.base import (
    WIDGET_RESULT_MODE_EDIT,
    WIDGET_RESULT_MODE_MESSAGE,
    WidgetResultMode,
)

MULTI_SELECT_DONE_KEY: Final[str] = "multi_select_done"
CHECKTABLE_STATE_KEY: Final[str] = "checktable_state"
CHECKTABLE_FIELD_KEY: Final[str] = "field"
CHECKTABLE_SET_COMMAND: Final[str] = "/_checktable-set"
CHECKTABLE_CLEAR_COMMAND: Final[str] = "/_checktable-clear"

WIDGET_COMMANDS_TEXT: Final[str] = "\n".join(
    [
        "Widget demos (new):",
        "/confirm-demo",
        "/select-demo",
        "/multi-select-demo",
        "/search-select-demo [query]",
        "/form-demo [text]",
        "/date-range-demo",
        "/table-demo [query]",
        "/approval-demo",
        "/async-job-demo [queued|running|failed|done]",
        "/file-batch-demo",
        "",
        "Widget demos (from pybotx-widgets):",
        "/calendar-demo",
        "/carousel-demo",
        "/checklist-demo",
        "/checktable-demo",
        "/range-demo",
        "/pagination-demo",
        "/messages-pager-demo",
    ],
)

DEFAULT_DEMO_RESULT_MODE: Final[WidgetResultMode] = WIDGET_RESULT_MODE_EDIT
DEMO_RESULT_MODE_BY_COMMAND: Final[dict[str, WidgetResultMode]] = {
    # Example:
    # "/confirm-demo": WIDGET_RESULT_MODE_MESSAGE,
}

SELECT_OPTIONS: Final[list[str | SelectOption]] = [
    SelectOption(value="dev", label="Development"),
    SelectOption(value="stage", label="Staging"),
    SelectOption(value="prod", label="Production"),
]

SEARCH_OPTIONS: Final[list[str | SelectOption]] = [
    SelectOption(value="alice", label="Alice Smith"),
    SelectOption(value="alex", label="Alex Johnson"),
    SelectOption(value="bob", label="Bob Lee"),
    SelectOption(value="chris", label="Chris Kim"),
    SelectOption(value="diana", label="Diana Ford"),
    SelectOption(value="elena", label="Elena Morgan"),
]

FORM_STEPS: Final[list[FormWizardStep]] = [
    FormWizardStep(field="name", label="Enter your name"),
    FormWizardStep(field="email", label="Enter your email"),
    FormWizardStep(field="team", label="Enter your team"),
]

TABLE_ROWS: Final[list[dict[str, str]]] = [
    {"name": "Alice", "team": "Platform", "role": "Engineer"},
    {"name": "Bob", "team": "Platform", "role": "Team Lead"},
    {"name": "Chris", "team": "QA", "role": "Engineer"},
    {"name": "Diana", "team": "Security", "role": "Engineer"},
    {"name": "Elena", "team": "Analytics", "role": "Analyst"},
]

DEFAULT_BATCH_FILES: Final[list[BatchFileItem]] = [
    BatchFileItem(name="sales_2026_01.csv", status="done"),
    BatchFileItem(name="sales_2026_02.csv", status="failed", error="bad header"),
    BatchFileItem(name="sales_2026_03.csv", status="running"),
    BatchFileItem(name="sales_2026_04.csv", status="pending"),
    BatchFileItem(name="sales_2026_05.csv", status="failed", error="timeout"),
]

ALLOWED_ASYNC_STATUSES: Final[set[str]] = {
    ASYNC_JOB_QUEUED,
    ASYNC_JOB_RUNNING,
    ASYNC_JOB_DONE,
    ASYNC_JOB_FAILED,
    ASYNC_JOB_CANCELLED,
}

CHECKTABLE_OWNER_VALUES: Final[list[str]] = ["Alice", "Bob", "Diana"]
CHECKTABLE_PRIORITY_LABELS: Final[dict[str, str]] = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
}
CHECKTABLE_NOTES_VALUES: Final[list[str]] = [
    "Needs product approval",
    "No additional notes",
]

PAGINATION_ITEMS: Final[list[str]] = [
    "Log line #1: accepted",
    "Log line #2: validated",
    "Log line #3: transformed",
    "Log line #4: uploaded",
    "Log line #5: indexed",
    "Log line #6: completed",
]

MESSAGES_PAGER_ITEMS: Final[list[str]] = [
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
]


def _multi_select_done_result(widget: MultiSelectWidget) -> str | None:
    if not widget.message.data.get(MULTI_SELECT_DONE_KEY):
        return None

    selected_items_list = MultiSelectWidget.get_selected_values(widget.message)
    selected_items = ", ".join(selected_items_list) or "nothing"
    return f"Selected values: {selected_items}"


def _form_after(widget: FormWizardWidget) -> str | None:
    if widget.is_completed:
        values_text = ", ".join(f"{key}={value}" for key, value in widget.values.items())
        return f"Form completed: {values_text}"

    if widget.cancelled:
        return "Form cancelled. Click reset to start over."

    return None


def _is_date_range_completed(widget: DateRangeWidget) -> bool:
    return widget.start is not None and widget.end is not None


def _date_range_result(widget: DateRangeWidget) -> str:
    assert widget.start is not None
    assert widget.end is not None
    return f"Date range selected: {widget.start.isoformat()} .. {widget.end.isoformat()}"


def _build_file_batch_widget(
    message: IncomingMessage,
    bot: Bot,
    files: list[BatchFileItem],
) -> FileBatchWidget:
    widget_files: list[BatchFileItem | dict[str, object] | str] = [
        file_item for file_item in files
    ]
    return FileBatchWidget(
        files=widget_files,
        label="Batch import status",
        page_size=3,
        message=message,
        bot=bot,
        command="/file-batch-demo",
        result_mode=_demo_result_mode("/file-batch-demo"),
    )


def _file_batch_retry_hook(widget: FileBatchWidget) -> RunnerHookResult:
    retried_files = _retry_failed_files(widget.files)
    return RunnerHookResult(
        widget=_build_file_batch_widget(widget.message, widget.bot, retried_files),
        should_display=True,
    )


async def _calendar_selected_result(widget: CalendarWidget) -> str:
    selected_date = await CalendarWidget.get_value(
        widget.message,
        widget.bot,
        send_feedback=False,
    )
    return f"Selected date: {selected_date.isoformat()}"


async def _carousel_selected_result(widget: CarouselWidget) -> str | None:
    selected_value = await CarouselWidget.get_value(
        widget.message,
        widget.bot,
        send_feedback=False,
    )
    if selected_value is None:
        return None

    return f"Carousel selected: {selected_value}"


def _range_after(widget: RangeWidget) -> str | None:
    if CURRENT_INDEX_KEY not in widget.message.data:
        return None

    if widget.result_mode != WIDGET_RESULT_MODE_MESSAGE:
        return None

    current_value = RangeWidget.get_value(widget.message)
    return f"Current stage: {current_value}"


def _build_checktable_widget(
    message: IncomingMessage,
    bot: Bot,
    state: dict[str, str],
) -> ChecktableWidget:
    message.metadata[CHECKTABLE_STATE_KEY] = dict(state)

    checkboxes: list[CheckboxContent[str]] = [
        CheckboxContent[str](
            label="Owner",
            command=CHECKTABLE_SET_COMMAND,
            checkbox_value=state.get("owner", undefined),
            data={CHECKTABLE_FIELD_KEY: "owner"},
        ),
        CheckboxContent[str](
            label="Priority",
            command=CHECKTABLE_SET_COMMAND,
            checkbox_value=state.get("priority", undefined),
            mapping=CHECKTABLE_PRIORITY_LABELS,
            data={CHECKTABLE_FIELD_KEY: "priority"},
        ),
        CheckboxContent[str](
            label="Notes",
            command=CHECKTABLE_SET_COMMAND,
            checkbox_value=state.get("notes", undefined),
            data={CHECKTABLE_FIELD_KEY: "notes"},
        ),
    ]

    return ChecktableWidget(
        checkboxes=checkboxes,
        label="Ticket fields",
        uncheck_command=CHECKTABLE_CLEAR_COMMAND,
        message=message,
        bot=bot,
        command="/checktable-demo",
        result_mode=_demo_result_mode("/checktable-demo"),
    )


collector = HandlerCollector()


@collector.command("/widgets", description="List all widget demo commands")
async def widgets_handler(_: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(WIDGET_COMMANDS_TEXT)


@collector.command("/confirm-demo", description="Confirm widget demo")
@widget_command(
    before=on_action(
        lambda widget: ConfirmWidget.get_action(widget.message),
        {
            CONFIRM_ACTION: "Confirm result: confirmed",
            CANCEL_ACTION: "Confirm result: cancelled",
        },
    ),
)
async def confirm_demo_handler(message: IncomingMessage, bot: Bot) -> ConfirmWidget:
    return ConfirmWidget(
        label="Confirm deployment to production?",
        message=message,
        bot=bot,
        command="/confirm-demo",
        result_mode=_demo_result_mode("/confirm-demo"),
    )


@collector.command("/select-demo", description="Single select widget demo")
@widget_command(
    before=on_data_key(
        SELECT_VALUE_KEY,
        lambda widget: (
            f"Selected environment: {SelectWidget.get_value(widget.message)}"
        ),
    ),
)
async def select_demo_handler(message: IncomingMessage, bot: Bot) -> SelectWidget:
    return SelectWidget(
        options=SELECT_OPTIONS,
        label="Choose an environment",
        message=message,
        bot=bot,
        command="/select-demo",
        result_mode=_demo_result_mode("/select-demo"),
    )


@collector.command("/multi-select-demo", description="Multi select widget demo")
@widget_command(
    before=on_data_key(
        MULTI_SELECT_DONE_KEY,
        _multi_select_done_result,
    ),
)
async def multi_select_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> MultiSelectWidget:
    summary_bubbles = BubbleMarkup()
    summary_bubbles.add_button(
        command="/multi-select-demo",
        label="Finish selection",
        data={MULTI_SELECT_DONE_KEY: True},
    )

    return MultiSelectWidget(
        options=[
            SelectOption(value="email", label="Email notifications"),
            SelectOption(value="sms", label="SMS notifications"),
            SelectOption(value="push", label="Push notifications"),
        ],
        label="Choose up to 2 notification channels",
        max_selected=2,
        message=message,
        bot=bot,
        command="/multi-select-demo",
        additional_markup=MessageMarkup(bubbles=summary_bubbles),
        result_mode=_demo_result_mode("/multi-select-demo"),
    )


@collector.command("/search-select-demo", description="Search + select widget demo")
@widget_command(
    before=on_data_key(
        SELECT_VALUE_KEY,
        lambda widget: f"Selected user: {SelectWidget.get_value(widget.message)}",
    ),
)
async def search_select_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> SearchSelectWidget:
    return SearchSelectWidget(
        options=SEARCH_OPTIONS,
        label="Search user by name",
        page_size=3,
        message=message,
        bot=bot,
        command="/search-select-demo",
        result_mode=_demo_result_mode("/search-select-demo"),
    )


@collector.command("/form-demo", description="Form wizard widget demo")
@widget_command(after=_form_after)
async def form_demo_handler(message: IncomingMessage, bot: Bot) -> FormWizardWidget:
    return FormWizardWidget(
        steps=FORM_STEPS,
        label="Profile form",
        message=message,
        bot=bot,
        command="/form-demo",
        result_mode=_demo_result_mode("/form-demo"),
    )


@collector.command("/date-range-demo", description="Date range widget demo")
@widget_command(
    after=on_completed(_is_date_range_completed, _date_range_result),
)
async def date_range_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> DateRangeWidget:
    return DateRangeWidget(
        label="Pick start and end dates",
        message=message,
        bot=bot,
        command="/date-range-demo",
        result_mode=_demo_result_mode("/date-range-demo"),
    )


@collector.command("/table-demo", description="Table widget demo")
@widget_command
async def table_demo_handler(message: IncomingMessage, bot: Bot) -> TableWidget:
    return TableWidget(
        rows=TABLE_ROWS,
        columns=["name", "team", "role"],
        label="Team directory",
        page_size=2,
        message=message,
        bot=bot,
        command="/table-demo",
        result_mode=_demo_result_mode("/table-demo"),
    )


@collector.command("/approval-demo", description="Approval widget demo")
@widget_command(
    before=on_action(
        lambda widget: ApprovalWidget.get_action(widget.message),
        {
            "approve": "Approval action: approve",
            "reject": "Approval action: reject",
            "comment": "Approval action: comment",
        },
    ),
)
async def approval_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> ApprovalWidget:
    return ApprovalWidget(
        label="Approve release candidate #42?",
        message=message,
        bot=bot,
        command="/approval-demo",
        result_mode=_demo_result_mode("/approval-demo"),
    )


@collector.command("/async-job-demo", description="Async job widget demo")
@widget_command
async def async_job_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> AsyncJobWidget:
    status, details = _resolve_async_job_state(message)

    return AsyncJobWidget(
        job_id=_resolve_job_id(message),
        status=status,
        details=details,
        message=message,
        bot=bot,
        command="/async-job-demo",
        result_mode=_demo_result_mode("/async-job-demo"),
    )


@collector.command("/file-batch-demo", description="File batch widget demo")
@widget_command(
    before=on_action(
        lambda widget: FileBatchWidget.get_action(widget.message),
        {
            FILE_BATCH_ACTION_ITEM: (
                lambda widget: (
                    f"Selected file: {FileBatchWidget.get_selected_file(widget.message)}"
                )
            ),
            FILE_BATCH_ACTION_RETRY_FAILED: _file_batch_retry_hook,
        },
    ),
)
async def file_batch_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> FileBatchWidget:
    initial_files = _load_batch_files(message)
    return _build_file_batch_widget(message, bot, initial_files)


@collector.command("/calendar-demo", description="Calendar widget demo")
@widget_command(
    before=on_data_key(
        CALENDAR_SELECTED_DATE_KEY,
        _calendar_selected_result,
    ),
)
async def calendar_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> CalendarWidget:
    return CalendarWidget(
        include_past=True,
        message=message,
        bot=bot,
        command="/calendar-demo",
        result_mode=_demo_result_mode("/calendar-demo"),
    )


@collector.command("/carousel-demo", description="Carousel widget demo")
@widget_command(
    before=on_data_key(
        CAROUSEL_SELECTED_VALUE_KEY,
        _carousel_selected_result,
    ),
)
async def carousel_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> CarouselWidget:
    return CarouselWidget(
        widget_content=["Paris", "Berlin", "Prague", "Rome", "Madrid", "Lisbon"],
        label="Choose a city",
        displayed_content_count=3,
        loop=False,
        inline=True,
        message=message,
        bot=bot,
        command="/carousel-demo",
        result_mode=_demo_result_mode("/carousel-demo"),
    )


@collector.command("/checklist-demo", description="Checklist widget demo")
@widget_command
async def checklist_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> CheckListWidget:
    checked_before = CheckListWidget.get_checked_items(message)
    widget = CheckListWidget(
        widget_content=["Build", ["Deploy", "Verify"], "Notify"],
        label=f"Release checklist (checked: {len(checked_before)})",
        message=message,
        bot=bot,
        command="/checklist-demo",
        result_mode=_demo_result_mode("/checklist-demo"),
    )
    widget.widget_message.body = f"Release checklist (checked: {len(widget.checked_items)})"
    return widget


@collector.command("/checktable-demo", description="Checktable widget demo")
@widget_command
async def checktable_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> ChecktableWidget:
    state = _read_checktable_state(message)
    return _build_checktable_widget(message, bot, state)


@collector.command(CHECKTABLE_SET_COMMAND, visible=False)
@widget_command
async def checktable_set_handler(
    message: IncomingMessage,
    bot: Bot,
) -> ChecktableWidget:
    state = _read_checktable_state(message)
    field = str(message.data.get(CHECKTABLE_FIELD_KEY, ""))

    if field == "owner":
        state[field] = _next_value(state.get(field), CHECKTABLE_OWNER_VALUES)
    elif field == "priority":
        priority_keys = list(CHECKTABLE_PRIORITY_LABELS)
        state[field] = _next_value(state.get(field), priority_keys)
    elif field == "notes":
        state[field] = _next_value(state.get(field), CHECKTABLE_NOTES_VALUES)

    return _build_checktable_widget(message, bot, state)


@collector.command(CHECKTABLE_CLEAR_COMMAND, visible=False)
@widget_command
async def checktable_clear_handler(
    message: IncomingMessage,
    bot: Bot,
) -> ChecktableWidget:
    state = _read_checktable_state(message)
    field = str(message.data.get(CHECKTABLE_FIELD_KEY, ""))
    state.pop(field, None)
    return _build_checktable_widget(message, bot, state)


@collector.command("/range-demo", description="Range widget demo")
@widget_command(after=_range_after)
async def range_demo_handler(message: IncomingMessage, bot: Bot) -> RangeWidget:
    return RangeWidget(
        elements=["Draft", "Review", "Approved", "Done"],
        label_template="Current stage {index}/{total}: {element}",
        message=message,
        bot=bot,
        command="/range-demo",
        result_mode=_demo_result_mode("/range-demo"),
    )


@collector.command("/pagination-demo", description="Pagination widget demo")
@widget_command
async def pagination_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> PaginationWidget:
    widget_content: list[OutgoingMessage | str] = [item for item in PAGINATION_ITEMS]
    return PaginationWidget(
        widget_content=widget_content,
        paginate_by=3,
        delay_between_messages=0,
        message=message,
        bot=bot,
        command="/pagination-demo",
        result_mode=_demo_result_mode("/pagination-demo"),
    )


@collector.command("/messages-pager-demo", description="Messages pager widget demo")
@widget_command
async def messages_pager_demo_handler(
    message: IncomingMessage,
    bot: Bot,
) -> MessagesPagerWidget:
    return MessagesPagerWidget(
        elements=MESSAGES_PAGER_ITEMS,
        page_size=2,
        item_template="Message {index}/{total}: {element}",
        delay_between_messages=0,
        message=message,
        bot=bot,
        command="/messages-pager-demo",
        result_mode=_demo_result_mode("/messages-pager-demo"),
    )


@collector.default_message_handler
async def default_message_handler(_: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message("Unknown command. Use /widgets to open demos.")


def _demo_result_mode(command: str) -> WidgetResultMode:
    return DEMO_RESULT_MODE_BY_COMMAND.get(command, DEFAULT_DEMO_RESULT_MODE)


def _read_checktable_state(message: IncomingMessage) -> dict[str, str]:
    raw_state = message.metadata.get(CHECKTABLE_STATE_KEY)
    if not isinstance(raw_state, dict):
        return {}

    state: dict[str, str] = {}
    for field in ("owner", "priority", "notes"):
        value = raw_state.get(field)
        if isinstance(value, str) and value:
            state[field] = value

    return state


def _next_value(current: str | None, values: list[str]) -> str:
    if current not in values:
        return values[0]

    current_index = values.index(current)
    next_index = (current_index + 1) % len(values)
    return values[next_index]

def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value

    raise RuntimeError(f"Environment variable {name} is required")


def _resolve_job_id(message: IncomingMessage) -> str:
    metadata_value = message.metadata.get(ASYNC_JOB_ID_KEY)
    if isinstance(metadata_value, str) and metadata_value:
        return metadata_value

    return "job-42"


def _resolve_async_job_state(message: IncomingMessage) -> tuple[str, str]:
    status = _resolve_initial_async_status(message)

    if ASYNC_JOB_ACTION_KEY not in message.data:
        return status, "Use widget buttons to move the async job state."

    action = AsyncJobWidget.get_action(message)

    if action == ASYNC_JOB_ACTION_CANCEL:
        return ASYNC_JOB_CANCELLED, "Job cancelled by user."

    if action == ASYNC_JOB_ACTION_RETRY:
        return ASYNC_JOB_QUEUED, "Retry requested."

    if action != ASYNC_JOB_ACTION_REFRESH:
        return status, "Unknown action."

    if status == ASYNC_JOB_QUEUED:
        return ASYNC_JOB_RUNNING, "Job picked by worker."

    if status == ASYNC_JOB_RUNNING:
        return ASYNC_JOB_DONE, "Job finished successfully."

    if status == ASYNC_JOB_FAILED:
        return ASYNC_JOB_FAILED, "Job still failed, click Retry."

    if status == ASYNC_JOB_CANCELLED:
        return ASYNC_JOB_CANCELLED, "Job is already cancelled."

    return ASYNC_JOB_DONE, "Job already done."


def _resolve_initial_async_status(message: IncomingMessage) -> str:
    raw_status = message.metadata.get(ASYNC_JOB_STATUS_KEY)
    if isinstance(raw_status, str) and raw_status in ALLOWED_ASYNC_STATUSES:
        return raw_status

    argument = message.argument.strip().lower()
    if argument in ALLOWED_ASYNC_STATUSES:
        return argument

    return ASYNC_JOB_QUEUED


def _load_batch_files(message: IncomingMessage) -> list[BatchFileItem]:
    raw_files = message.metadata.get(FILE_BATCH_FILES_KEY)
    if not isinstance(raw_files, list):
        return list(DEFAULT_BATCH_FILES)

    files: list[BatchFileItem] = []
    for raw_item in raw_files:
        if not isinstance(raw_item, dict):
            continue

        name = raw_item.get("name")
        status = raw_item.get("status")
        if name is None or status is None:
            continue

        files.append(
            BatchFileItem(
                name=str(name),
                status=str(status),
                error=str(raw_item.get("error", "")),
            ),
        )

    if not files:
        return list(DEFAULT_BATCH_FILES)

    return files


def _retry_failed_files(files: list[BatchFileItem]) -> list[BatchFileItem]:
    retried_files: list[BatchFileItem] = []

    for file_item in files:
        if file_item.status in {"failed", "error"}:
            retried_files.append(
                BatchFileItem(
                    name=file_item.name,
                    status="running",
                    error="",
                ),
            )
            continue

        retried_files.append(file_item)

    return retried_files


def _build_bot_from_env() -> Bot:
    account = BotAccountWithSecret(

    )
    return Bot(
        collectors=[collector],
        bot_accounts=[account],
    )


bot = _build_bot_from_env()

app = FastAPI()
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)


@app.post("/command")
async def command_handler(request: Request) -> JSONResponse:
    bot.async_execute_raw_bot_command(
        await request.json(),
        request_headers=request.headers,
    )
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )


@app.get("/status")
async def status_handler(request: Request) -> JSONResponse:
    status = await bot.raw_get_status(
        dict(request.query_params),
        request_headers=request.headers,
    )
    return JSONResponse(status)


@app.post("/notification/callback")
async def callback_handler(request: Request) -> JSONResponse:
    await bot.set_raw_botx_method_result(
        await request.json(),
        verify_request=False,
    )
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )
