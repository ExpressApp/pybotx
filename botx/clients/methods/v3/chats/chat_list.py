"""Method for retrieving information about chat."""
from http import HTTPStatus

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import messaging
from botx.models.chats import BotChatList


class ChatList(AuthorizedBotXMethod[BotChatList]):  # noqa: WPS110
    """Method for retrieving list of bot chats."""

    __url__ = "/api/v3/botx/chats/list"
    __method__ = "GET"
    __returning__ = BotChatList
