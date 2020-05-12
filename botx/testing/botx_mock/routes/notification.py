"""Endpoints for notification resource."""

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.methods.v3.notification.notification import Notification
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.messages import add_message_to_collection
from botx.testing.botx_mock.responses import generate_push_response


@bind_implementation_to_method(Notification)
async def post_notification(request: Request) -> Response:
    """Handle pushed notification request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = Notification.parse_obj(await request.json())
    add_message_to_collection(request, payload)
    return JSONResponse(APIResponse[str](result="notification_pushed").dict())


@bind_implementation_to_method(NotificationDirect)
async def post_notification_direct(request: Request) -> Response:
    """Handle pushed notification request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = NotificationDirect.parse_obj(await request.json())
    add_message_to_collection(request, payload)
    return generate_push_response(payload)
