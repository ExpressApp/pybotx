"""Definition for "image not valid" error."""
from typing import NoReturn

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class ImageNotValidError(BotXAPIError):
    """Error for raising when image not valid."""

    message_template = "image not valid"


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "image not valid" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        ImageNotValidError: raised always.
    """
    APIErrorResponse[dict].parse_obj(response.json_body)
    raise ImageNotValidError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
    )
