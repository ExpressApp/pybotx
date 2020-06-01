"""Mixin for shortcut for chats resource requests."""

from typing import List, Optional
from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.chats.add_user import AddUser
from botx.clients.methods.v3.chats.create import Create
from botx.clients.methods.v3.chats.info import Info
from botx.clients.methods.v3.chats.remove_user import RemoveUser
from botx.clients.methods.v3.chats.stealth_disable import StealthDisable
from botx.clients.methods.v3.chats.stealth_set import StealthSet
from botx.models.chats import ChatFromSearch
from botx.models.enums import ChatTypes
from botx.models.messages.sending.credentials import SendingCredentials


class ChatsRequestsMixin:
    """Mixin for shortcut for chats resource requests."""

    async def create_chat(  # noqa: WPS211
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        name: str,
        members: List[UUID],
        chat_type: ChatTypes,
        description: Optional[str] = None,
        avatar: Optional[str] = None,
    ) -> UUID:
        """Create new chat.

        Arguments:
            credentials: credentials for making request.
            name: name of chat that should be created.
            members: HUIDs of users that should be added into chat.
            chat_type: chat type.
            description: description of new chat.
            avatar: logo image of chat.

        Returns:
             ID of created chat.
        """
        return await self.call_method(
            Create(
                name=name,
                description=description,
                members=members,
                avatar=avatar,
                chat_type=chat_type,
            ),
            credentials=credentials,
        )

    async def get_chat_info(
        self: BotXMethodCallProtocol, credentials: SendingCredentials, chat_id: UUID,
    ) -> ChatFromSearch:
        """Create new chat.

        Arguments:
            credentials: credentials for making request.
            chat_id: ID of chat for about which information should be retrieving.

        Returns:
             Information about chat.
        """
        return await self.call_method(
            Info(group_chat_id=chat_id), credentials=credentials,
        )

    async def enable_stealth_mode(  # noqa: WPS211
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        chat_id: UUID,
        disable_web: bool = False,
        burn_in: Optional[int] = None,
        expire_in: Optional[int] = None,
    ) -> None:
        """Enable stealth mode.

        Arguments:
            credentials: credentials for making request.
            chat_id: ID of chat where stealth should be enabled.
            disable_web: should messages be shown in web.
            burn_in: time of messages burning after read.
            expire_in: time of messages burning after send.
        """
        await self.call_method(
            StealthSet(
                group_chat_id=chat_id,
                disable_web=disable_web,
                burn_in=burn_in,
                expire_in=expire_in,
            ),
            credentials=credentials,
        )

    async def disable_stealth_mode(
        self: BotXMethodCallProtocol, credentials: SendingCredentials, chat_id: UUID,
    ) -> None:
        """Disable stealth mode.

        Arguments:
            credentials: credentials for making request.
            chat_id: ID of chat where stealth should be disabled.
        """
        await self.call_method(
            StealthDisable(group_chat_id=chat_id), credentials=credentials,
        )

    async def add_users(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        chat_id: UUID,
        user_huids: List[UUID],
    ) -> None:
        """Add users to chat.

        Arguments:
            credentials: credentials for making request.
            chat_id: ID of chat into which users should be added.
            user_huids: IDs of users that should be added into chat.
        """
        await self.call_method(
            AddUser(group_chat_id=chat_id, user_huids=user_huids),
            credentials=credentials,
        )

    async def remove_users(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        chat_id: UUID,
        user_huids: List[UUID],
    ) -> None:
        """Remove users from chat.

        Arguments:
            credentials: credentials for making request.
            chat_id: ID of chat from which users should be removed.
            user_huids: HUID of users that should be removed.
        """
        await self.call_method(
            RemoveUser(group_chat_id=chat_id, user_huids=user_huids),
            credentials=credentials,
        )
