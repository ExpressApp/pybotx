"""Endpoints for bots resource."""

from starlette.requests import Request
from starlette.responses import Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v2.bots.token import Token
from botx.testing.botx_mock.asgi.messages import add_request_to_collection
from botx.testing.botx_mock.asgi.responses import PydanticResponse
from botx.testing.botx_mock.binders import bind_implementation_to_method


@bind_implementation_to_method(Token)
async def get_token(request: Request) -> Response:
    """Handle retrieving token from BotX API request.

    Arguments:
        request: starlette request for route.

    Returns:
        Return response with new token.
    """
    request_data = {**request.path_params, **request.query_params}
    payload = Token(**request_data)
    add_request_to_collection(request, payload)
    return PydanticResponse(APIResponse[str](result="real token"))
