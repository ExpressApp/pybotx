from typing import NoReturn

from httpx import Response

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.exceptions import BotXAPIError


class ChatCreationError(BotXAPIError):
    message_template = "error while creating chat"


def handle_error(method: BotXMethod, response: Response) -> NoReturn:
    APIErrorResponse[dict](**response.json())
    raise ChatCreationError(
        url=method.url,
        method=method.__method__,
        response_content=response.content,
        status_content=response.status_code,
    )
