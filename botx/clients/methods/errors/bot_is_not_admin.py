from typing import NoReturn
from uuid import UUID

from httpx import Response
from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.exceptions import BotXAPIError


class BotIsNotAdminError(BotXAPIError):
    message_template = "bot {bot_id} is not admin of chat {group_chat_id}"

    sender: UUID
    group_chat_id: UUID


class BotIsNotAdminData(BaseModel):
    sender: UUID
    group_chat_id: UUID


def handle_error(method: BotXMethod, response: Response) -> NoReturn:
    error_data = APIErrorResponse[BotIsNotAdminData](**response.json())
    raise BotIsNotAdminError(
        url=method.url,
        method=method.method,
        response_content=response.content,
        status_content=response.status_code,
        sender=error_data.error_data.sender,
        group_chat_id=error_data.error_data.group_chat_id,
    )
