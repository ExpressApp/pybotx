"""Method for removing users from chat."""
from typing import List
from uuid import UUID

from httpx import StatusCode

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import (
    bot_is_not_admin,
    chat_is_not_modifiable,
    chat_not_found,
)


class RemoveUser(AuthorizedBotXMethod[bool]):
    """Method for removing users from chat."""

    __url__ = "/api/v3/botx/chats/remove_user"
    __method__ = "POST"
    __returning__ = bool
    __errors_handlers__ = {
        StatusCode.FORBIDDEN: (
            bot_is_not_admin.handle_error,
            chat_is_not_modifiable.handle_error,
        ),
        StatusCode.NOT_FOUND: (chat_not_found.handle_error,),
    }

    #: ID of chat from which users should be removed.
    group_chat_id: UUID

    #: HUID of users that should be removed.
    user_huids: List[UUID]
