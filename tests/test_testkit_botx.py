import pytest

from pybotx.domain.errors import TestkitConfigurationError as BotxTestkitConfigurationError
from pybotx.testkit.botx import BotXRequest, _default_headers, mock_botx


def test__default_headers__with_json() -> None:
    headers = _default_headers(has_json=True)

    assert headers["Authorization"] == "Bearer token"
    assert headers["Content-Type"] == "application/json"


def test__default_headers__without_json() -> None:
    headers = _default_headers(has_json=False)

    assert headers == {"Authorization": "Bearer token"}


def test__mock_botx__response_content(respx_mock) -> None:
    request = BotXRequest(method="GET", path="/ping")

    route = mock_botx(
        respx_mock,
        "example.org",
        request,
        response_json=None,
        response_content="pong",
    )

    assert route is not None


def test__mock_botx__empty_response(respx_mock) -> None:
    request = BotXRequest(method="GET", path="/ping")

    route = mock_botx(
        respx_mock,
        "example.org",
        request,
        response_json=None,
        response_content=None,
    )

    assert route is not None


def test__mock_botx__no_auth_no_headers(respx_mock) -> None:
    request = BotXRequest(method="GET", path="/ping", require_auth=False)

    route = mock_botx(
        respx_mock,
        "example.org",
        request,
        response_json={"ok": True},
        response_content=None,
    )

    assert route is not None


def test__mock_botx__conflicting_response() -> None:
    request = BotXRequest(method="GET", path="/ping")

    with pytest.raises(BotxTestkitConfigurationError):
        mock_botx(
            respx_mock=None,  # type: ignore[arg-type]
            host="example.org",
            request=request,
            response_json={"ok": True},
            response_content=b"data",
        )
