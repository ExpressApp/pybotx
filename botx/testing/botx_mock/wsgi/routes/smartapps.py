"""Endpoints for smartapps."""

from molten import RequestData, Response, Settings

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.smartapps.smartapp_event import SmartAppEvent
from botx.clients.methods.v3.smartapps.smartapp_notification import SmartAppNotification
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.wsgi.messages import add_message_to_collection
from botx.testing.botx_mock.wsgi.responses import PydanticResponse


@bind_implementation_to_method(SmartAppEvent)
def post_smartapp_event(request_data: RequestData, settings: Settings) -> Response:
    """Handle pushed smartapp event request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = SmartAppEvent.parse_obj(request_data)
    add_message_to_collection(settings, payload)
    return PydanticResponse(APIResponse[str](result="smartapp_event_pushed"))


@bind_implementation_to_method(SmartAppNotification)
def post_smartapp_notification(
    request_data: RequestData,
    settings: Settings,
) -> Response:
    """Handle pushed smartapp notification request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = SmartAppNotification.parse_obj(request_data)
    add_message_to_collection(settings, payload)
    return PydanticResponse(APIResponse[str](result="smartapp_notification_pushed"))
