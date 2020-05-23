from uuid import UUID

from httpx import StatusCode

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import messaging
from botx.clients.types.chats import ChatFromSearch


class Info(AuthorizedBotXMethod[ChatFromSearch]):
    __url__ = "/api/v3/botx/chats/info"
    __method__ = "GET"
    __returning__ = ChatFromSearch
    __error_handlers__ = {StatusCode.BAD_REQUEST: messaging.handle_error}

    group_chat_id: UUID
