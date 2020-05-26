from typing import NoReturn

from httpx import Response

from botx.clients.methods.base import APIErrorResponse, BotXMethod
from botx.exceptions import BotXAPIError


class UserNotFoundError(BotXAPIError):
    message_template = "user not found"


def handle_error(method: BotXMethod, response: Response) -> NoReturn:
    APIErrorResponse[dict].parse_obj(response.json())
    raise UserNotFoundError(
        url=method.url,
        method=method.http_method,
        response_content=response.content,
        status_content=response.status_code,
    )
