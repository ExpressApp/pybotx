"""Definition for "messaging" error."""
from typing import NoReturn

from httpx import Response

from botx.clients.methods.base import BotXMethod
from botx.exceptions import BotXAPIError


class MessagingError(BotXAPIError):
    """Error for raising when there is messaging error."""

    message_template = "error from messaging service"


def handle_error(method: BotXMethod, response: Response) -> NoReturn:
    """Handle messaging error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        MessagingError: raised always.
    """
    raise MessagingError(
        url=method.url,
        method=method.http_method,
        response=response.json(),
        status=response.status_code,
    )
