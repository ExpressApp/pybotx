"""Definition for "no permission" error."""
from typing import NoReturn
from uuid import UUID

from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class NoPermissionError(BotXAPIError):
    """Error for raising when there is no permission for operation."""

    message_template = (
        "Bot doesn't have permission for this operation in chat {group_chat_id}"
    )

    #: ID of chat that was requested.
    group_chat_id: UUID


class NoPermissionErrorData(BaseModel):
    """Data for error when there is no permission for operation."""

    #: ID of chat that was requested.
    group_chat_id: UUID


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "no permission" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        NoPermissionError: raised always.
    """
    parsed_response = APIErrorResponse[NoPermissionErrorData].parse_obj(
        response.json_body,
    )

    error_data = parsed_response.error_data
    raise NoPermissionError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
        group_chat_id=error_data.group_chat_id,
    )
