"""Endpoints for smartapps."""

from starlette.requests import Request
from starlette.responses import Response

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.smartapps.smartapp_event import SmartAppEvent
from botx.clients.methods.v3.smartapps.smartapp_notification import SmartAppNotification
from botx.testing.botx_mock.asgi.messages import add_message_to_collection
from botx.testing.botx_mock.asgi.responses import PydanticResponse
from botx.testing.botx_mock.binders import bind_implementation_to_method


@bind_implementation_to_method(SmartAppEvent)
async def post_smartapp_event(request: Request) -> Response:
    """Handle pushed smartapp event request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = SmartAppEvent.parse_obj(await request.json())
    add_message_to_collection(request, payload)
    return PydanticResponse(APIResponse[str](result="smartapp_event_pushed"))


@bind_implementation_to_method(SmartAppNotification)
async def post_smartapp_notification(request: Request) -> Response:
    """Handle pushed smartapp notification request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = SmartAppNotification.parse_obj(await request.json())
    add_message_to_collection(request, payload)
    return PydanticResponse(APIResponse[str](result="smartapp_notification_pushed"))
