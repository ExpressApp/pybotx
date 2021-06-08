"""Definition for "chat is not modifiable" error."""
from typing import NoReturn
from uuid import UUID

from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.clients.types.http import HTTPResponse
from botx.exceptions import BotXAPIError


class PersonalChatIsNotModifiableError(BotXAPIError):
    """Error for raising when chat is not modifiable."""

    message_template = "personal chat is not modifiable"


class PersonalChatIsNotModifiableData(BaseModel):
    """Data for error when chat is not modifiable."""

    #: ID of chat that can not be modified.
    group_chat_id: UUID


def handle_error(method: BotXMethod, response: HTTPResponse) -> NoReturn:
    """Handle "chat creation error" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        PersonalChatIsNotModifiableError: raised always.
    """
    parsed_response = APIErrorResponse[PersonalChatIsNotModifiableData].parse_obj(
        response.json_body,
    )
    error_data = parsed_response.error_data
    raise PersonalChatIsNotModifiableError(
        url=method.url,
        method=method.http_method,
        response_content=response.json_body,
        status_content=response.status_code,
        group_chat_id=error_data.group_chat_id,
    )
