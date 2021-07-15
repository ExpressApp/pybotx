"""Definition for "bot not found" error."""
from typing import NoReturn

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class BotNotFoundError(BotXAPIError):
    """Error for raising when bot not found."""

    message_template = "bot with id `{bot_id}` not found. "


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "bot not found" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        BotNotFoundError: raised always.
    """
    APIErrorResponse[dict].parse_obj(response.json_body)
    raise BotNotFoundError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
        bot_id=method.bot_id,  # type: ignore
    )
