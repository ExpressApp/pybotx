from typing import NoReturn
from uuid import UUID

from httpx import Response
from pydantic import BaseModel

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.exceptions import BotXAPIError


class ChatNotFoundError(BotXAPIError):
    message_template = "chat {group_chat_id} not found"

    group_chat_id: UUID


class ChatNotFoundData(BaseModel):
    group_chat_id: UUID


def handle_error(method: BotXMethod, response: Response) -> NoReturn:
    parsed_response = APIErrorResponse[ChatNotFoundData].parse_obj(response.json())

    error_data = parsed_response.error_data
    raise ChatNotFoundError(
        url=method.url,
        method=method.http_method,
        response_content=response.content,
        status_content=response.status_code,
        group_chat_id=error_data.group_chat_id,
    )
