import json
from typing import TYPE_CHECKING, Any

from loguru import logger as _logger

if TYPE_CHECKING:  # To avoid circular import
    from loguru import Logger


def pformat_jsonable_obj(jsonable_obj: Any) -> str:
    return json.dumps(jsonable_obj, sort_keys=True, indent=4, ensure_ascii=False)


def setup_logger() -> "Logger":
    _logger.disable("httpx")

    return _logger


logger = setup_logger()
