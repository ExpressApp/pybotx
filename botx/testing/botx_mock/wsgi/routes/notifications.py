"""Endpoints for notifications resource."""
from molten import RequestData, Response, Settings

from botx.clients.methods.v4.notifications.internal_bot_notification import (
    InternalBotNotification,
)
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.wsgi.messages import add_message_to_collection
from botx.testing.botx_mock.wsgi.responses import (
    generate_internal_bot_notification_response,
)


@bind_implementation_to_method(InternalBotNotification)
def post_internal_bot_notification(
    request_data: RequestData,
    settings: Settings,
) -> Response:
    """Handle pushed notification request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = InternalBotNotification.parse_obj(request_data)
    add_message_to_collection(settings, payload)
    return generate_internal_bot_notification_response(payload)
