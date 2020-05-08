"""Logic for extending messages and requests collections from test client."""

import contextlib

from starlette.requests import Request

from botx.testing.typing import APIMessage, APIRequest


def add_message_to_collection(request: Request, message: APIMessage) -> None:
    """Add new message to messages collection.

    Arguments:
          request: request from Starlette endpoint.
          message: message that should be added.
    """
    app = request.app
    with contextlib.suppress(AttributeError):
        app.state.messages.append(message)

    add_request_to_collection(request, message)


def add_request_to_collection(http_request: Request, api_request: APIRequest) -> None:
    """Add new API request to requests collection.

    Arguments:
          http_request: request from Starlette endpoint.
          api_request: API request that should be added.
    """
    app = http_request.app
    with contextlib.suppress(AttributeError):
        app.state.requests.append(api_request)
