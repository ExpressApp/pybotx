from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Mapping, Optional, Union, cast

import httpx
from deepdiff import DeepDiff
from respx.router import MockRouter, Route  # type: ignore[attr-defined]


@dataclass(frozen=True)
class BotXRequest:
    method: str
    path: str
    json: Optional[dict[str, Any]] = None
    params: Optional[dict[str, Any]] = None
    headers: Optional[Mapping[str, str]] = None
    require_auth: bool = True


def _default_headers(*, has_json: bool) -> dict[str, str]:
    headers = {"Authorization": "Bearer token"}
    if has_json:
        headers["Content-Type"] = "application/json"
    return headers


def mock_botx(
    respx_mock: MockRouter,
    host: str,
    request: BotXRequest,
    response_json: Optional[Union[dict[str, Any], list[Any]]],
    status: int = HTTPStatus.OK,
    response_content: Optional[Union[bytes, str]] = None,
) -> Route:
    if response_json is not None and response_content is not None:
        raise ValueError("Provide either response_json or response_content, not both.")

    headers = request.headers
    if headers is None and request.require_auth:
        headers = _default_headers(has_json=request.json is not None)

    route_kwargs: dict[str, Any] = {}
    if headers is not None:
        route_kwargs["headers"] = headers
    if request.json is not None:
        route_kwargs["json"] = request.json
    if request.params is not None:
        route_kwargs["params"] = request.params

    route = cast(
        Route,
        getattr(respx_mock, request.method.lower())(
            f"https://{host}{request.path}",
            **route_kwargs,
        ),
    )
    if response_json is not None:
        route.mock(return_value=httpx.Response(status, json=response_json))
        return route
    if response_content is None:
        route.mock(return_value=httpx.Response(status))
        return route
    route.mock(return_value=httpx.Response(status, content=response_content))
    return route


def ok_payload(result: Any) -> dict[str, Any]:
    return {"status": "ok", "result": result}


def error_payload(
    reason: str,
    *,
    error_data: Optional[dict[str, Any]] = None,
    errors: Optional[list[str]] = None,
) -> dict[str, Any]:
    return {
        "status": "error",
        "reason": reason,
        "errors": errors or [],
        "error_data": error_data or {},
    }


def assert_deep_equal(
    actual: Any,
    expected: Any,
    *,
    ignore_order: bool = True,
) -> None:
    diff = DeepDiff(actual, expected, ignore_order=ignore_order)
    assert diff == {}
