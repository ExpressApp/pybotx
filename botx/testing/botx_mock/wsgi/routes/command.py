"""Endpoints for command resource."""
from molten import RequestData, Response, Settings

from botx.clients.methods.v3.command.command_result import CommandResult
from botx.testing.botx_mock.binders import bind_implementation_to_method
from botx.testing.botx_mock.wsgi.messages import add_message_to_collection
from botx.testing.botx_mock.wsgi.responses import generate_push_response


@bind_implementation_to_method(CommandResult)
def post_command_result(request_data: RequestData, settings: Settings) -> Response:
    """Handle command result request.

    Arguments:
        request_data: parsed json data from request.
        settings: application settings with storage.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = CommandResult.parse_obj(request_data)
    add_message_to_collection(settings, payload)
    return generate_push_response(payload)
