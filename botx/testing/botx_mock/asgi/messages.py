"""Logic for extending messages and requests collections from test client."""

import contextlib

from starlette.requests import Request

from botx.clients.methods.base import BotXMethod


def add_message_to_collection(request: Request, message: BotXMethod) -> None:
    """Add new message to messages collection.

    Arguments:
          request: request from Starlette endpoint.
          message: message that should be added.
    """
    app = request.app
    with contextlib.suppress(AttributeError):
        app.state.messages.append(message)

    add_request_to_collection(request, message)


def add_request_to_collection(http_request: Request, api_request: BotXMethod) -> None:
    """Add new API request to requests collection.

    Arguments:
          http_request: request from Starlette endpoint.
          api_request: API request that should be added.
    """
    app = http_request.app
    with contextlib.suppress(AttributeError):
        app.state.requests.append(api_request)
