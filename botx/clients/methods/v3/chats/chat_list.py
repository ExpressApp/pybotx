"""Method for retrieving information about chat."""

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.models.chats import BotChatList


class ChatList(AuthorizedBotXMethod[BotChatList]):  # noqa: WPS110
    """Method for retrieving list of bot's chats."""

    __url__ = "/api/v3/botx/chats/list"
    __method__ = "GET"
    __returning__ = BotChatList
