from uuid import UUID

from httpx import StatusCode

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import messaging


class Info(AuthorizedBotXMethod[str]):
    __url__ = "/api/v3/botx/chats/info"
    __method__ = "GET"
    __returning__ = str
    __error_handlers__ = {StatusCode.BAD_REQUEST: messaging.handle_error}

    group_chat_id: UUID
