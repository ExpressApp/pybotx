"""Definition of middleware that will generate BotX API errors depending from flag."""
from typing import Tuple, Type

from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.testing.botx_mock.asgi.responses import PydanticResponse


def _fill_request_scope(request: Request) -> None:
    routes = request.app.router.routes
    for route in routes:
        match, scope = route.matches(request)
        if match == Match.FULL:
            request.scope = {**request.scope, **scope}


def _get_error_from_request(
    request: Request,
) -> Tuple[Type[BotXMethod], Tuple[int, BaseModel]]:
    _fill_request_scope(request)
    endpoint = request.scope["endpoint"]
    method = endpoint.method
    return method, request.app.state.errors.get(method)


def should_generate_error_response(request: Request) -> bool:
    """Check if mocked API should generate error response.

    Arguments:
        request: request from Starlette route that contains application with required
            state.

    Returns:
        Result of check.
    """
    _, status_and_error_to_raise = _get_error_from_request(request)
    return bool(status_and_error_to_raise)


def generate_error_response(request: Request) -> Response:
    """Generate error response for mocked BotX API.

    Arguments:
        request: request from Starlette route that contains application with required
            state.

    Returns:
        Generated response.
    """
    method, response_info = _get_error_from_request(request)
    status_code, error_data = response_info

    return PydanticResponse(
        APIErrorResponse[BaseModel](
            errors=["error from mock"], reason="asked_for_error", error_data=error_data,
        ),
        status_code=status_code,
    )


class ErrorMiddleware(BaseHTTPMiddleware):
    """Middleware that will generate error response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint,
    ) -> Response:
        """Generate error response for API call or pass request to mocked endpoint.

        Arguments:
            request: request that should be handled.
            call_next: next executor for mock.

        Returns:
              Mocked response.
        """
        if should_generate_error_response(request):
            return generate_error_response(request)

        return await call_next(request)
