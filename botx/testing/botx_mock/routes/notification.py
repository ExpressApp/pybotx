"""Endpoints for notification resource."""

from starlette.requests import Request
from starlette.responses import Response

from botx.models.requests import Notification
from botx.testing.botx_mock.messages import add_message_to_collection
from botx.testing.botx_mock.responses import generate_push_response


async def post_notification_direct(request: Request) -> Response:
    """Handle pushed notification request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = Notification.parse_obj(await request.json())
    add_message_to_collection(request, payload)
    return generate_push_response(payload)
