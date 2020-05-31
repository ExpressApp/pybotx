"""Endpoints for bots resource."""
from uuid import UUID

from molten import Request, Response, Settings

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v2.bots.token import Token
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.wsgi.messages import add_request_to_collection
from botx.testing.botx_mock.wsgi.responses import PydanticResponse


@bind_implementation_to_method(Token)
def get_token(bot_id: str, request: Request, settings: Settings) -> Response:
    """Handle retrieving token from BotX API request.

    Arguments:
        bot_id: ID of bot from query params.
        request: modten request for route.
        settings: application settings with storage.

    Returns:
        Return response with new token.
    """
    signature = request.params["signature"]
    payload = Token(bot_id=UUID(bot_id), signature=signature)
    add_request_to_collection(settings, payload)
    return PydanticResponse(APIResponse[str](result="real token"))
