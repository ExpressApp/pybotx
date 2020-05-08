"""Definition of middleware that will generate BotX API errors depending from flag."""

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


def should_generate_error_response(request: Request) -> bool:
    """Check if mocked API should generate error response.

    Arguments:
        request: request from Starlette route that contains application with required
            state.

    Returns:
        Result of check.
    """
    app = request.app
    return app.state.generate_errors


def generate_error_response() -> Response:
    """Generate error response for mocked BotX API.

    Returns:
        Generated response.
    """
    return JSONResponse(
        {"result": "API error"}, status_code=status.HTTP_400_BAD_REQUEST
    )


class ErrorMiddleware(BaseHTTPMiddleware):
    """Middleware that will generate error response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Generate error response for API call or pass request to mocked endpoint.

        Arguments:
            request: request that should be handled.
            call_next: next executor for mock.

        Returns:
              Mocked response.
        """
        if should_generate_error_response(request):
            return generate_error_response()

        return await call_next(request)
