"""Endpoints for events resource."""
from molten import RequestData, Response, Settings

from botx.clients.methods.base import APIResponse
from botx.clients.methods.v3.events.edit_event import EditEvent
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.wsgi.messages import add_message_to_collection
from botx.testing.botx_mock.wsgi.responses import PydanticResponse


@bind_implementation_to_method(EditEvent)
def post_edit_event(request_data: RequestData, settings: Settings) -> Response:
    """Handle edition of event request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Empty json response.
    """
    payload = EditEvent.parse_obj(request_data)
    add_message_to_collection(settings, payload)
    return PydanticResponse(APIResponse[str](result="update_pushed"))
