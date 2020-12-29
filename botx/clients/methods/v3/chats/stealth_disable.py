"""Method for disabling stealth in chat."""
from http import HTTPStatus
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import bot_is_not_admin, chat_not_found


class StealthDisable(AuthorizedBotXMethod[bool]):
    """Method for disabling stealth in chat."""

    __url__ = "/api/v3/botx/chats/stealth_disable"
    __method__ = "POST"
    __returning__ = bool
    __errors_handlers__ = {
        HTTPStatus.FORBIDDEN: bot_is_not_admin.handle_error,
        HTTPStatus.NOT_FOUND: chat_not_found.handle_error,
    }

    #: ID of chat where stealth should be disabled.
    group_chat_id: UUID
