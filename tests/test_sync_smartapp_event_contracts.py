import pytest

from pybotx.domain.models.sync_smartapp_event import (
    SyncSmartAppEventError,
    SyncSmartAppEventResult,
)
from pybotx.presentation.contracts.sync_smartapp_event import (
    BotAPISyncSmartAppEventErrorResponse,
    BotAPISyncSmartAppEventResultResponse,
    convert_sync_smartapp_event_response,
)


def test__convert_sync_smartapp_event_response__api_passthrough() -> None:
    response = BotAPISyncSmartAppEventResultResponse.from_domain(data={"ok": True})
    assert convert_sync_smartapp_event_response(response) is response


def test__convert_sync_smartapp_event_response__error_passthrough() -> None:
    response = BotAPISyncSmartAppEventErrorResponse.from_domain(reason="boom")
    assert convert_sync_smartapp_event_response(response) is response


def test__convert_sync_smartapp_event_response__domain_result() -> None:
    response = SyncSmartAppEventResult(data={"value": 1}, files=None)
    converted = convert_sync_smartapp_event_response(response)

    assert isinstance(converted, BotAPISyncSmartAppEventResultResponse)


def test__convert_sync_smartapp_event_response__domain_error() -> None:
    response = SyncSmartAppEventError(reason="reason", errors=["e"], error_data={})
    converted = convert_sync_smartapp_event_response(response)

    assert isinstance(converted, BotAPISyncSmartAppEventErrorResponse)


def test__convert_sync_smartapp_event_response__unsupported_type() -> None:
    with pytest.raises(TypeError):
        convert_sync_smartapp_event_response(object())
