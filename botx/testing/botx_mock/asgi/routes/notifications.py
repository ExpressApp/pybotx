"""Endpoints for notification resource."""

from starlette.requests import Request
from starlette.responses import Response

from botx.clients.methods.v4.notifications.internal_bot_notification import (
    InternalBotNotification,
)
from botx.testing.botx_mock.asgi.messages import add_message_to_collection
from botx.testing.botx_mock.asgi.responses import (
    generate_internal_bot_notification_response,
)
from botx.testing.botx_mock.binders import bind_implementation_to_method


@bind_implementation_to_method(InternalBotNotification)
async def post_internal_bot_notification(request: Request) -> Response:
    """Handle pushed notification request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = InternalBotNotification.parse_obj(await request.json())
    add_message_to_collection(request, payload)
    return generate_internal_bot_notification_response(payload)
