"""Definition for "chat creating disallowed" error."""
from typing import NoReturn
from uuid import UUID

from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class ChatCreationDisallowedError(BotXAPIError):
    """Error for raising when bot is not allowed to create chats."""

    message_template = "bot {bot_id} is not allowed to create chats"

    #: ID of bot that sent request.
    bot_id: UUID


class ChatCreationDisallowedData(BaseModel):
    """Data for error when bot is not allowed to create chats."""

    #: ID of bot that sent request.
    bot_id: UUID


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "chat creating disallowed" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        ChatCreationDisallowedError: raised always.
    """
    parsed_response = APIErrorResponse[ChatCreationDisallowedData].parse_obj(
        response.json_body,
    )
    error_data = parsed_response.error_data
    raise ChatCreationDisallowedError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
        bot_id=error_data.bot_id,
    )
