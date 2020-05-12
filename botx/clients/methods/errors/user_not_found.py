from typing import NoReturn

from httpx import Response

from botx import BotXAPIError
from botx.clients.methods.base import APIErrorResponse, BotXMethod


class UserNotFoundError(BotXAPIError):
    message_template = "user not found"


def handle_error(method: BotXMethod, response: Response) -> NoReturn:
    APIErrorResponse[dict](**response.json())  # check that response shape is right
    raise UserNotFoundError(
        url=method.url,
        method=method.method,
        response_content=response.content,
        status_content=response.status_code,
    )
