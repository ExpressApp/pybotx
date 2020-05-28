"""Definition for "bot is not admin" error."""
from typing import NoReturn
from uuid import UUID

from httpx import Response
from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.exceptions import BotXAPIError


class BotIsNotAdminError(BotXAPIError):
    """Error for raising when bot is not admin."""

    message_template = "bot {bot_id} is not admin of chat {group_chat_id}"

    #: ID of bot that sent request.
    bot_id: UUID

    #: ID of chat into which request was sent.
    group_chat_id: UUID


class BotIsNotAdminData(BaseModel):
    """Data for error when bot is not admin."""

    #: ID of sender (bot)
    sender: UUID

    #: ID of chat into which request was sent.
    group_chat_id: UUID


def handle_error(method: BotXMethod, response: Response) -> NoReturn:
    """Handle "bot is not admin" error response.

    Arguments:
        method: method which was made before error.
        response: HTTP response from BotX API.

    Raises:
        BotIsNotAdminError: raised always.
    """
    error_data = (
        APIErrorResponse[BotIsNotAdminData].parse_obj(response.json()).error_data
    )
    raise BotIsNotAdminError(
        url=method.url,
        method=method.http_method,
        response_content=response.content,
        status_content=response.status_code,
        bot_id=error_data.sender,
        group_chat_id=error_data.group_chat_id,
    )
