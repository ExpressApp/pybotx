"""Endpoints for events resource."""

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.events.edit_event import EditEvent
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.messages import add_message_to_collection


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
    return JSONResponse(APIResponse[str](result="update_pushed").dict())
