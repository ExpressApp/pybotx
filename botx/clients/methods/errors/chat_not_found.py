"""Definition for "chat not found" error."""
from typing import NoReturn
from uuid import UUID

from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class ChatNotFoundError(BotXAPIError):
    """Error for raising when chat not found."""

    message_template = "chat {group_chat_id} not found"

    #: ID of chat that was requested.
    group_chat_id: UUID


class ChatNotFoundData(BaseModel):
    """Data for error when chat not found."""

    #: ID of chat that was requested.
    group_chat_id: UUID


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "chat creation error" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        ChatNotFoundError: raised always.
    """
    parsed_response = APIErrorResponse[ChatNotFoundData].parse_obj(response.json_body)

    error_data = parsed_response.error_data
    raise ChatNotFoundError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
        group_chat_id=error_data.group_chat_id,
    )
