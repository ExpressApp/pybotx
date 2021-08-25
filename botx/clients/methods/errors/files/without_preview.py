"""Definition for "without preview" error."""
from typing import NoReturn
from uuid import UUID

from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class WithoutPreviewError(BotXAPIError):
    """Error for raising when there is no file preview."""

    message_template = "{error_description}"

    #: description of error.
    error_description: str


class WithoutPreviewData(BaseModel):
    """Data for error when there is no file preview."""

    #: ID of file which preview was requested.
    file_id: UUID

    #: ID of chat where file is from.
    group_chat_id: UUID

    #: description of error.
    error_description: str


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "without preview" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        WithoutPreviewError: raised always.
    """
    parsed_response = APIErrorResponse[WithoutPreviewData].parse_obj(response.json_body)

    error_data = parsed_response.error_data
    raise WithoutPreviewError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
        error_description=error_data.error_description,
    )
