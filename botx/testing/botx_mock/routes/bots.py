"""Endpoints for bots resource."""

from starlette.requests import Request
from starlette.responses import Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v2.bots.token import Token
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.messages import add_request_to_collection
from botx.testing.botx_mock.responses import PydanticResponse


@bind_implementation_to_method(Token)
async def get_token(request: Request) -> Response:
    """Handle retrieving token from BotX API request.

    Returns:
        Return request with new token.
    """
    payload = Token(**request.path_params, **request.query_params)
    add_request_to_collection(request, payload)
    return PydanticResponse(APIResponse[str](result="real token"))
