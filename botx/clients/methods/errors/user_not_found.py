"""Definition for "user not found" error."""
from typing import NoReturn

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class UserNotFoundError(BotXAPIError):
    """Error for raising when user not found."""

    message_template = "user not found"


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "user not found" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        UserNotFoundError: raised always.
    """
    APIErrorResponse[dict].parse_obj(response.json_body)
    raise UserNotFoundError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
    )
