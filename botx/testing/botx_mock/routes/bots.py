"""Endpoints for bots resource."""

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v2.bots.token import Token
from botx.testing.botx_mock.binders import bind_implementation_to_method


@bind_implementation_to_method(Token)
async def get_token(_: Request) -> Response:
    """Handle retrieving token from BotX API request.

    Returns:
        Return request with new token.
    """
    return JSONResponse(APIResponse[str](result="real token").dict())


GetToken = (Token, get_token)
