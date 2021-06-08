"""Definition for "chat creation error"."""
from typing import NoReturn

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class ChatCreationError(BotXAPIError):
    """Error for raising when there is error for chat creation."""

    message_template = "error while creating chat"


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "chat creation error" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        ChatCreationError: raised always.
    """
    APIErrorResponse[dict].parse_obj(response.json_body)
    raise ChatCreationError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
    )
