"""Definition for "image is not valid" error."""
from typing import NoReturn

from botx.clients.methods.base import BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class ImageNotValidError(BotXAPIError):
    """Error for raising when image is not valid."""

    message_template = "image is not valid"


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "image is not valid" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        ImageNotValidError: raised always.
    """
    raise ImageNotValidError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
    )
