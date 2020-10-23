"""Method for enabling stealth in chat."""
from typing import Optional
from uuid import UUID

import httpx

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import bot_is_not_admin, chat_not_found


class StealthSet(AuthorizedBotXMethod[bool]):
    """Method for enabling stealth in chat."""

    __url__ = "/api/v3/botx/chats/stealth_set"
    __method__ = "POST"
    __returning__ = bool
    __errors_handlers__ = {
        httpx.codes.FORBIDDEN: bot_is_not_admin.handle_error,
        httpx.codes.NOT_FOUND: chat_not_found.handle_error,
    }

    #: ID of chat where stealth should be enabled.
    group_chat_id: UUID

    #: should messages be shown in web.
    disable_web: bool = False

    #: time of messages burning after read.
    burn_in: Optional[int] = None

    #: time of messages burning after send.
    expire_in: Optional[int] = None
