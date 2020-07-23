"""Definition of middleware that will generate BotX API errors depending from flag."""
from typing import Any, Callable, Tuple, Type, cast

from httpx import StatusCode
from molten import BaseApp, Request, Response, Route, Settings
from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.testing.botx_mock.wsgi.responses import PydanticResponse


def _get_error_from_request(
    request: Request, app: BaseApp, settings: Settings,
) -> Tuple[Type[BotXMethod], Tuple[int, BaseModel]]:
    match = app.router.match(request.method, request.path)
    route, _ = cast(Tuple[Route, Any], match)
    method = route.handler.method  # type: ignore
    return method, settings["errors"].get(method)


def should_generate_error_response(
    request: Request, app: BaseApp, settings: Settings,
) -> bool:
    """Check if mocked API should generate error response.

    Arguments:
        request: request from molten route.
        app: molten app that serves request.
        settings: application settings with storage.

    Returns:
        Result of check.
    """
    _, status_and_error_to_raise = _get_error_from_request(request, app, settings)
    return bool(status_and_error_to_raise)


def generate_error_response(
    request: Request, app: BaseApp, settings: Settings,
) -> Response:
    """Generate error response for mocked BotX API.

    Arguments:
        request: request from molten route.
        app: molten app that serves request.
        settings: application settings with storage.

    Returns:
        Generated response.
    """
    method, response_info = _get_error_from_request(request, app, settings)
    status_code, error_data = response_info

    return PydanticResponse(
        APIErrorResponse[BaseModel](
            errors=["error from mock"], reason="asked_for_error", error_data=error_data,
        ),
        status_code="{0} {1}".format(
            status_code, StatusCode.get_reason_phrase(status_code),
        ),
    )


def error_middleware(handler: Callable[..., Any]) -> Callable[..., Any]:
    """Middleware that will generate error response.

    Arguments:
        handler: next handler for request for molten.

    Returns:
        Created handler for request.
    """

    def decorator(request: Request, app: BaseApp, settings: Settings) -> Any:
        if should_generate_error_response(request, app, settings):
            return generate_error_response(request, app, settings)

        return handler()

    return decorator
