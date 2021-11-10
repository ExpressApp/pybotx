"""Method for unpinning message in chat."""
from http import HTTPStatus
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import chat_not_found, permissions


class UnpinMessage(AuthorizedBotXMethod[str]):
    """Method for unpinning message in chat."""

    __url__ = "/api/v3/botx/chats/unpin_message"
    __method__ = "POST"
    __returning__ = str
    __errors_handlers__ = {
        HTTPStatus.NOT_FOUND: chat_not_found.handle_error,
        HTTPStatus.FORBIDDEN: permissions.handle_error,
    }

    #: ID of chat where message should be unpinned.
    chat_id: UUID
