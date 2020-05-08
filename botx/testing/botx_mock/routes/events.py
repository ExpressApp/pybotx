"""Endpoints for events resource."""

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from botx.models.requests import EventEdition
from botx.testing.botx_mock.messages import add_message_to_collection


async def post_edit_event(request: Request) -> Response:
    """Handle edition of event request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Empty json response.
    """
    payload = EventEdition.parse_obj(await request.json()).result
    add_message_to_collection(request, payload)
    return JSONResponse({})
