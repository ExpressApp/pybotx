from contextvars import Token
from typing import Any, cast
from uuid import UUID

import pytest

from pybotx.bot.contextvars import bot_id_var, chat_id_var, request_id_var, trace_id_var
from pybotx.logger import _inject_correlation_fields, _is_env_enabled, logger


def test__logger__injects_correlation_fields_from_contextvars() -> None:
    bot_id_token: Token[UUID] = bot_id_var.set(UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"))
    chat_id_token: Token[UUID] = chat_id_var.set(UUID("d4d3d774-1f90-4b53-9b92-7f3867dbb2f8"))
    request_id_token: Token[str] = request_id_var.set("request-id")
    trace_id_token: Token[str] = trace_id_var.set("trace-id")
    record: dict[str, dict[str, str | None]] = {"extra": {}}

    try:
        _inject_correlation_fields(record)
    finally:
        trace_id_var.reset(trace_id_token)
        request_id_var.reset(request_id_token)
        chat_id_var.reset(chat_id_token)
        bot_id_var.reset(bot_id_token)

    assert record["extra"]["request_id"] == "request-id"
    assert record["extra"]["trace_id"] == "trace-id"
    assert record["extra"]["bot_id"] == "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"
    assert record["extra"]["chat_id"] == "d4d3d774-1f90-4b53-9b92-7f3867dbb2f8"


def test__logger__inject_does_not_override_existing_fields() -> None:
    record = {
        "extra": {
            "trace_id": "existing-trace",
            "request_id": "existing-request",
            "bot_id": "existing-bot",
            "chat_id": "existing-chat",
        },
    }

    _inject_correlation_fields(record)

    assert record["extra"] == {
        "trace_id": "existing-trace",
        "request_id": "existing-request",
        "bot_id": "existing-bot",
        "chat_id": "existing-chat",
    }


def test__logger__structured_json_by_default() -> None:
    handler = next(iter(cast(Any, logger)._core.handlers.values()))

    assert getattr(handler, "_serialize", None) is True


def test__logger__is_env_enabled_uses_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PYBOTX_LOG_STRUCTURED", raising=False)
    assert _is_env_enabled("PYBOTX_LOG_STRUCTURED", default=True) is True
    assert _is_env_enabled("PYBOTX_LOG_STRUCTURED", default=False) is False


def test__logger__is_env_enabled_parses_false_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PYBOTX_LOG_STRUCTURED", "off")
    assert _is_env_enabled("PYBOTX_LOG_STRUCTURED", default=True) is False
