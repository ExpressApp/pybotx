from typing import NoReturn
from uuid import UUID

from httpx import Response
from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.exceptions import BotXAPIError


class ChatCreationDisallowedError(BotXAPIError):
    message_template = "bot {bot_id} is not allowed to create chats"

    bot_id: UUID


class ChatCreationDisallowedData(BaseModel):
    bot_id: UUID


def handle_error(method: BotXMethod, response: Response) -> NoReturn:
    error_data = APIErrorResponse[ChatCreationDisallowedData](
        **response.json()
    ).error_data
    raise ChatCreationDisallowedError(
        url=method.url,
        method=method.__method__,
        response_content=response.content,
        status_content=response.status_code,
        bot_id=error_data.bot_id,
    )
