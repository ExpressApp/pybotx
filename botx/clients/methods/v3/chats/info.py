"""Method for retrieving information about chat."""
from http import HTTPStatus
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import messaging
from botx.models.chats import ChatFromSearch


class Info(AuthorizedBotXMethod[ChatFromSearch]):  # noqa: WPS110
    """Method for retrieving information about chat."""

    __url__ = "/api/v3/botx/chats/info"
    __method__ = "GET"
    __returning__ = ChatFromSearch
    __errors_handlers__ = {HTTPStatus.BAD_REQUEST: messaging.handle_error}

    #: ID of chat for about which information should be retrieving.
    group_chat_id: UUID
