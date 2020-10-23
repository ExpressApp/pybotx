"""Method for promoting users to admins."""
from typing import List
from uuid import UUID

import httpx

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.errors import (
    bot_is_not_admin,
    chat_is_not_modifiable,
    chat_not_found,
)


class AddAdminRole(AuthorizedBotXMethod[bool]):
    """Method for promoting users to chat admins."""

    __url__ = "/api/v3/botx/chats/add_admin"
    __method__ = "POST"
    __returning__ = bool
    __errors_handlers__ = {
        httpx.codes.FORBIDDEN: (
            bot_is_not_admin.handle_error,
            chat_is_not_modifiable.handle_error,
        ),
        httpx.codes.NOT_FOUND: (chat_not_found.handle_error,),
    }

    #: ID of chat where action should be performed.
    group_chat_id: UUID

    #: IDs of users that should be promoted to admins.
    user_huids: List[UUID]
