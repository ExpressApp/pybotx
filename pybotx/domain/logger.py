import json
from copy import deepcopy
from typing import Any

from loguru import logger as _logger

from pybotx.domain.constants import MAX_FILE_LEN_IN_LOGS
from pybotx.domain.ports.logger import LoggerPort


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


class _LoggerProxy(LoggerPort):
    def __init__(self, target: LoggerPort) -> None:
        self._target = target

    def set_target(self, target: LoggerPort) -> None:
        self._target = target

    def add(self, *args: Any, **kwargs: Any) -> Any:
        return self._target.add(*args, **kwargs)

    def remove(self, *args: Any, **kwargs: Any) -> None:
        self._target.remove(*args, **kwargs)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._target.debug(message, *args, **kwargs)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._target.info(message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._target.warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._target.error(message, *args, **kwargs)

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._target.exception(message, *args, **kwargs)

    def opt(self, *args: Any, **kwargs: Any) -> LoggerPort:
        return _LoggerProxy(self._target.opt(*args, **kwargs))

    def enable(self, name: str) -> None:
        self._target.enable(name)

    def disable(self, name: str) -> None:
        self._target.disable(name)


def setup_logger() -> LoggerPort:
    return _logger


_logger_proxy = _LoggerProxy(setup_logger())
logger: LoggerPort = _logger_proxy


def set_logger(new_logger: LoggerPort) -> None:
    _logger_proxy.set_target(new_logger)


def get_logger() -> LoggerPort:
    return _logger_proxy
