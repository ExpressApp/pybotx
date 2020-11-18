"""Endpoints for notification resource."""
from molten import RequestData, Response, Settings

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.methods.v3.notification.notification import Notification
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.wsgi.messages import add_message_to_collection
from botx.testing.botx_mock.wsgi.responses import (
    PydanticResponse,
    generate_push_response,
)


@bind_implementation_to_method(Notification)
def post_notification(request_data: RequestData, settings: Settings) -> Response:
    """Handle pushed notification request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = Notification.parse_obj(request_data)
    add_message_to_collection(settings, payload)
    return PydanticResponse(APIResponse[str](result="notification_pushed"))


@bind_implementation_to_method(NotificationDirect)
def post_notification_direct(request_data: RequestData, settings: Settings) -> Response:
    """Handle pushed notification request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = NotificationDirect.parse_obj(request_data)
    add_message_to_collection(settings, payload)
    return generate_push_response(payload)
