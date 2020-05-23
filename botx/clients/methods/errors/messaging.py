from typing import NoReturn

from httpx import Response

from botx import BotXAPIError
from botx.clients.methods.base import BotXMethod


class MessagingError(BotXAPIError):
    message_template = "error from messaging service"


def handle_error(method: BotXMethod, response: Response) -> NoReturn:
    raise MessagingError(
        url=method.url,
        method=method.__method__,
        response=response.json(),
        status=response.status_code,
    )
