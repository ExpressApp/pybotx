"""Definition for mixin that defines BotX API methods."""

from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from botx.clients.methods.v3.chats.add_user import AddUser
from botx.clients.methods.v3.chats.remove_user import RemoveUser
from botx.clients.methods.v3.chats.stealth_disable import StealthDisable
from botx.clients.methods.v3.chats.stealth_set import StealthSet
from botx.models import sending

if TYPE_CHECKING:
    from botx.bots.bot import Bot  # noqa: WPS433


class ChatsRequestsMixin:
    """Mixin that defines methods for communicating with BotX API."""

    async def stealth_enable(
        self: "Bot",
        credentials: sending.SendingCredentials,
        chat_id: UUID,
        disable_web: bool,
        burn_in: Optional[int],
        expire_in: Optional[int],
    ) -> None:
        """Enable stealth mode

        Arguments:
            credentials: credentials of chat.
            chat_id: id of chat to enable stealth,
            disable_web: disable web client for chat,
            burn_in: time to burn,
            expire_in: time to expire,
        """
        return await self.call_method(
            StealthSet(
                group_chat_id=chat_id,
                disable_web=disable_web,
                burn_in=burn_in,
                expire_in=expire_in,
            ),
            credentials=credentials,
        )

    async def stealth_disable(
        self: "Bot", credentials: sending.SendingCredentials, chat_id: UUID,
    ) -> None:
        """Disable stealth mode

        Arguments:
            credentials: credentials of chat.
            chat_id: id of chat to disable stealth,
        """
        return await self.call_method(
            StealthDisable(group_chat_id=chat_id), credentials=credentials
        )

    async def add_users(
        self: "Bot",
        credentials: sending.SendingCredentials,
        chat_id: UUID,
        users_huids: List[UUID],
    ) -> None:
        """Add users to chat.

        Arguments:
            credentials: credentials of chat.
            chat_id: id of chat to add users,
            users_huids: list of user's huids
        """
        return await self.call_method(
            AddUser(group_chat_id=chat_id, user_huids=users_huids),
            credentials=credentials,
        )

    async def remove_users(
        self: "Bot",
        credentials: sending.SendingCredentials,
        chat_id: UUID,
        users_huids: List[UUID],
    ) -> None:
        """Remove users from chat.

        Arguments:
            credentials: credentials of chat.
            chat_id: id of chat to remove users,
            users_huids: list of user's huids
        """
        return await self.call_method(
            RemoveUser(group_chat_id=chat_id, user_huids=users_huids),
            credentials=credentials,
        )
