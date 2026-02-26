# Widget Demo Bot

This folder contains a simple `pybotx` + FastAPI demo bot for all widgets in this repository:
both newly added and transferred from `pybotx-widgets`.

Full widgets documentation:

- `/Users/aleksandrosovskii/PycharmProjects/pybotx_stable/WIDGETS.md`

## What is included

`/Users/aleksandrosovskii/PycharmProjects/pybotx_stable/example/main.py` implements demos for:

- `ConfirmWidget`
- `SelectWidget`
- `MultiSelectWidget`
- `SearchSelectWidget`
- `FormWizardWidget`
- `DateRangeWidget`
- `TableWidget`
- `ApprovalWidget`
- `AsyncJobWidget`
- `FileBatchWidget`
- `CalendarWidget`
- `CarouselWidget`
- `CheckListWidget`
- `ChecktableWidget`
- `RangeWidget`
- `PaginationWidget`
- `MessagesPagerWidget`

## Requirements

Use the repository environment:

```bash
uv sync --dev
```

## Configuration

Set environment variables:

```bash
export BOT_ID="123e4567-e89b-12d3-a456-426655440000"
export BOT_CTS_URL="https://cts.example.com"
export BOT_SECRET_KEY="replace-with-real-secret"
```

## Run

```bash
uv run uvicorn example.main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

- `POST /command`
- `GET /status`
- `POST /notification/callback`

## Demo commands in chat

Send `/widgets` to get the full list of demo commands.

Result behavior (`edit` vs `message`) is configured in code, not by user command:

- `DEFAULT_DEMO_RESULT_MODE`
- `DEMO_RESULT_MODE_BY_COMMAND`

Both constants are in `/Users/aleksandrosovskii/PycharmProjects/pybotx_stable/example/main.py`.

All widget handlers are unified via `WidgetRunner` from `pybotx.widgets` and used in `/Users/aleksandrosovskii/PycharmProjects/pybotx_stable/example/main.py`.
