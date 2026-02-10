from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any

from pybotx.domain.errors import (
    BotXValidationError,
    InvalidWebhookPayloadError,
    UnknownBotAccountError,
    UnverifiedRequestError,
)
from pybotx.domain.logger import logger
from pybotx.presentation.api.responses.bot_disabled import build_bot_disabled_response
from pybotx.presentation.api.responses.unverified_request import (
    build_unverified_request_response,
)


def parse_json_body(body: bytes) -> dict[str, Any]:
    if not body:
        return {}
    payload = json.loads(body.decode("utf-8"))
    if not isinstance(payload, dict):
        raise InvalidWebhookPayloadError("Payload must be a JSON object")
    return payload


def map_botx_exception(
    exc: Exception,
    *,
    validation_label: str,
) -> tuple[int, dict[str, Any]] | None:
    if isinstance(exc, BotXValidationError):
        logger.exception(validation_label)
        return (
            HTTPStatus.SERVICE_UNAVAILABLE,
            build_bot_disabled_response(validation_label),
        )
    if isinstance(exc, UnknownBotAccountError):
        error_label = f"No credentials for bot {exc.bot_id}"
        logger.warning(error_label)
        return (
            HTTPStatus.SERVICE_UNAVAILABLE,
            build_bot_disabled_response(error_label),
        )
    if isinstance(exc, UnverifiedRequestError):
        message = exc.args[0] if exc.args else "Unverified request"
        return (
            HTTPStatus.UNAUTHORIZED,
            build_unverified_request_response(status_message=message),
        )
    return None
