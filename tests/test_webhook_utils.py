import json
from http import HTTPStatus
from uuid import uuid4

import pytest

from pybotx.domain.errors import (
    BotCommandValidationError,
    InvalidWebhookPayloadError,
    UnknownBotAccountError,
    UnverifiedRequestError,
)
from pybotx.presentation.api.responses.bot_disabled import build_bot_disabled_response
from pybotx.presentation.api.responses.unverified_request import (
    build_unverified_request_response,
)
from pybotx.presentation.webhook_utils import map_botx_exception, parse_json_body


def test__parse_json_body__empty() -> None:
    assert parse_json_body(b"") == {}


def test__parse_json_body__dict_payload() -> None:
    payload = {"ok": True}
    assert parse_json_body(json.dumps(payload).encode("utf-8")) == payload


def test__parse_json_body__non_dict() -> None:
    with pytest.raises(InvalidWebhookPayloadError):
        parse_json_body(b"\"text\"")


def test__map_botx_exception__validation_error() -> None:
    status_code, payload = map_botx_exception(
        BotCommandValidationError("bad"),
        validation_label="validation failed",
    )

    assert status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert payload == build_bot_disabled_response("validation failed")


def test__map_botx_exception__unknown_bot() -> None:
    bot_id = uuid4()
    status_code, payload = map_botx_exception(
        UnknownBotAccountError(bot_id),
        validation_label="ignored",
    )

    assert status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert payload == build_bot_disabled_response(f"No credentials for bot {bot_id}")


def test__map_botx_exception__unverified_request() -> None:
    status_code, payload = map_botx_exception(
        UnverifiedRequestError("bad token"),
        validation_label="ignored",
    )

    assert status_code == HTTPStatus.UNAUTHORIZED
    assert payload == build_unverified_request_response("bad token")


def test__map_botx_exception__unknown() -> None:
    assert (
        map_botx_exception(RuntimeError("oops"), validation_label="ignored") is None
    )
