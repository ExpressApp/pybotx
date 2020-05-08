"""Endpoints for bots resource."""

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from botx.models.responses import TokenResponse


async def get_token(_: Request) -> Response:
    """Handle retrieving token from BotX API request.

    Returns:
        Return request with new token.
    """
    return JSONResponse(TokenResponse(result="real token").dict())
