import json
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict

from loguru import logger as _logger

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


def trim_file_data_in_incoming_json(json_body: Dict[str, Any]) -> Dict[str, Any]:
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


def log_incoming_request(request: Dict[str, Any], *, message: str = "") -> None:
    logger.opt(lazy=True).debug(
        message + "{command}",
        command=lambda: pformat_jsonable_obj(
            trim_file_data_in_incoming_json(request),
        ),
    )


def setup_logger() -> "Logger":
    return _logger


logger = setup_logger()
