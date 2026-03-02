import json
import os
import sys
from copy import deepcopy
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any

from loguru import logger as _logger

from pybotx.bot.contextvars import bot_id_var, chat_id_var, request_id_var, trace_id_var
from pybotx.constants import MAX_FILE_LEN_IN_LOGS

if TYPE_CHECKING:  # To avoid circular import
    from loguru import Logger


def pformat_jsonable_obj(jsonable_obj: Any) -> str:
    return json.dumps(jsonable_obj, sort_keys=True, indent=4, ensure_ascii=False)


def trim_file_data_in_outgoing_json(json_body: Any) -> Any:
    if not isinstance(json_body, dict):
        return json_body

    if json_body.get("file"):
        json_body = deepcopy(json_body)
        json_body["file"]["data"] = (
            json_body["file"]["data"][:MAX_FILE_LEN_IN_LOGS] + "...<trimmed>"
        )

    return json_body


def trim_file_data_in_incoming_json(json_body: dict[str, Any]) -> dict[str, Any]:
    if json_body.get("attachments"):
        # Max one attach per-message
        # Link and Location doesn't have content
        if json_body["attachments"][0]["data"].get("content"):
            json_body = deepcopy(json_body)
            json_body["attachments"][0]["data"]["content"] = (
                json_body["attachments"][0]["data"]["content"][:MAX_FILE_LEN_IN_LOGS]
                + "...<trimmed>"
            )

    return json_body


def log_incoming_request(request: dict[str, Any], *, message: str = "") -> None:
    logger.opt(lazy=True).debug(
        message + "{command}",
        command=lambda: pformat_jsonable_obj(
            trim_file_data_in_incoming_json(request),
        ),
    )


def setup_logger() -> "Logger":
    logger = _logger.patch(_inject_correlation_fields)
    if _is_env_enabled("PYBOTX_CONFIGURE_LOGGER", default=True):
        logger.remove()
        logger.add(
            sys.stderr,
            level=os.getenv("PYBOTX_LOG_LEVEL", "DEBUG"),
            serialize=_is_env_enabled("PYBOTX_LOG_STRUCTURED", default=True),
            backtrace=False,
            diagnose=False,
        )
    return logger


def _inject_correlation_fields(record: Any) -> None:
    extra = record["extra"]
    extra.setdefault("trace_id", _get_optional_contextvar_value(trace_id_var))
    extra.setdefault("request_id", _get_optional_contextvar_value(request_id_var))
    extra.setdefault("chat_id", _get_optional_contextvar_value(chat_id_var))
    extra.setdefault("bot_id", _get_optional_contextvar_value(bot_id_var))


def _get_optional_contextvar_value(context_var: ContextVar[Any]) -> str | None:
    try:
        value = context_var.get()
    except LookupError:
        return None
    return str(value)


def _is_env_enabled(name: str, *, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.lower() not in {"0", "false", "no", "off"}


logger = setup_logger()
