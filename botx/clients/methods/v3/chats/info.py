"""Method for retrieving information about chat."""
from uuid import UUID

from httpx import StatusCode

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import messaging
from botx.models.chats import ChatFromSearch


class Info(AuthorizedBotXMethod[ChatFromSearch]):
    """Method for retrieving information about chat."""

    __url__ = "/api/v3/botx/chats/info"
    __method__ = "GET"
    __returning__ = ChatFromSearch
    __errors_handlers__ = {StatusCode.BAD_REQUEST: messaging.handle_error}

    #: ID of chat for about which information should be retrieving.
    group_chat_id: UUID
