"""Definition for "file metadata not found" error."""
from typing import NoReturn
from uuid import UUID

from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class MetadataNotFoundError(BotXAPIError):
    """Error for raising when file metadata not found."""

    message_template = (
        "File with specified file_id `{file_id}` and "
        "group_chat_id `{group_chat_id}` not found in file service."
    )

    #: ID of file which metadata was requested.
    file_id: UUID

    #: ID of chat where file is from.
    group_chat_id: UUID


class MetadataNotFoundData(BaseModel):
    """Data for error when file metadata not found."""

    #: ID of file which metadata was requested.
    file_id: UUID

    #: ID of chat where file is from.
    group_chat_id: UUID

    #: description of error.
    error_description: str


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "file metadata not found" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        MetadataNotFoundError: raised always.
    """
    parsed_response = APIErrorResponse[MetadataNotFoundData].parse_obj(
        response.json_body,
    )

    error_data = parsed_response.error_data
    raise MetadataNotFoundError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
        file_id=error_data.file_id,
        group_chat_id=error_data.group_chat_id,
    )
