"""Endpoints for events resource."""

from starlette.requests import Request
from starlette.responses import Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.events.edit_event import EditEvent
from botx.clients.methods.v3.events.reply_event import ReplyEvent
from botx.testing.botx_mock.asgi.messages import add_message_to_collection
from botx.testing.botx_mock.asgi.responses import PydanticResponse
from botx.testing.botx_mock.binders import bind_implementation_to_method


@bind_implementation_to_method(EditEvent)
async def post_edit_event(request: Request) -> Response:
    """Handle edition of event request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Empty json response.
    """
    payload = EditEvent.parse_obj(await request.json())
    add_message_to_collection(request, payload)
    return PydanticResponse(APIResponse[str](result="update_pushed"))


@bind_implementation_to_method(ReplyEvent)
async def post_reply_event(request: Request) -> Response:
    """Handle reply event request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Empty json response.
    """
    payload = ReplyEvent.parse_obj(await request.json())
    add_message_to_collection(request, payload)
    return PydanticResponse(APIResponse[str](result="reply_pushed"))
