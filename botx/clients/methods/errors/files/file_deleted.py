"""Definition for "file deleted" error."""
from typing import NoReturn

from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class FileDeletedError(BotXAPIError):
    """Error for raising when file deleted."""

    message_template = "{error_description}"

    #: description of error.
    error_description: str


class FileDeletedErrorData(BaseModel):
    """Data for error when file deleted."""

    #: link of deleted file.
    link: str

    #: description of error.
    error_description: str


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "file deleted" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        FileDeletedError: raised always.
    """
    parsed_response = APIErrorResponse[FileDeletedErrorData].parse_obj(
        response.json_body,
    )

    error_data = parsed_response.error_data
    raise FileDeletedError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
        error_description=error_data.error_description,
    )
