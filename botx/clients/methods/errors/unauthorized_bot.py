"""Definition for "invalid bot credentials" error."""
from typing import NoReturn

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class InvalidBotCredentials(BotXAPIError):
    """Error for raising when got invalid bot credentials."""

    message_template = (
        "Can't get token for bot {bot_id}. Make sure bot credentials is correct"
    )


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "invalid bot credentials" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        InvalidBotCredentials: raised always.
    """
    APIErrorResponse[dict].parse_obj(response.json_body)
    raise InvalidBotCredentials(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
        bot_id=method.bot_id,  # type: ignore
    )
