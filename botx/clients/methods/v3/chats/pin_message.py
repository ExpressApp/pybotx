"""Method for pinning message in chat."""
from http import HTTPStatus
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import chat_not_found, permissions


class PinMessage(AuthorizedBotXMethod[str]):
    """Method for pinning message in chat."""

    __url__ = "/api/v3/botx/chats/pin_message"
    __method__ = "POST"
    __returning__ = str
    __errors_handlers__ = {
        HTTPStatus.NOT_FOUND: chat_not_found.handle_error,
        HTTPStatus.FORBIDDEN: permissions.handle_error,
    }

    #: ID of chat where message should be pinned.
    chat_id: UUID

    #: ID of message that should be pinned.
    sync_id: UUID
