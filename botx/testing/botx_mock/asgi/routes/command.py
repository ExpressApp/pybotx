"""Endpoints for command resource."""

from starlette.requests import Request
from starlette.responses import Response

from botx.clients.methods.v3.command.command_result import CommandResult
from botx.testing.botx_mock.asgi.messages import add_message_to_collection
from botx.testing.botx_mock.asgi.responses import generate_push_response
from botx.testing.botx_mock.binders import bind_implementation_to_method


@bind_implementation_to_method(CommandResult)
async def post_command_result(request: Request) -> Response:
    """Handle command result request.

    Arguments:
        request: HTTP request from Starlette.

    Returns:
        Response with sync_id of pushed message.
    """
    payload = CommandResult.parse_obj(await request.json())
    add_message_to_collection(request, payload)
    return generate_push_response(payload)
