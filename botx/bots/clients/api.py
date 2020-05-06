"""Definition for mixin that defines BotX API methods."""
from typing import Awaitable, Callable, List, Optional
from uuid import UUID

from botx import clients
from botx.models import sending
from botx.models.credentials import ExpressServer, ServerCredentials
from botx.models.requests import (
    AddRemoveUsersPayload,
    StealthDisablePayload,
    StealthEnablePayload,
)


class APIMixin:
    known_hosts: List[ExpressServer]
    client: clients.AsyncClient
    _obtain_token: Callable[[sending.SendingCredentials], Awaitable[None]]

    async def update_message(
        self, credentials: sending.SendingCredentials, update: sending.UpdatePayload
    ) -> None:
        """Change message by it's event id.

        Arguments:
            credentials: credentials that are used for sending message. *sync_id* is
                required for credentials.
            update: update of message content.
        """
        await self._obtain_token(credentials)
        await self.client.edit_event(credentials, update)

    async def stealth_enable(
        self,
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
        await self._obtain_token(credentials)
        return await self.client.stealth_enable(
            credentials=credentials,
            payload=StealthEnablePayload(
                group_chat_id=chat_id,
                disable_web=disable_web,
                burn_in=burn_in,
                expire_in=expire_in,
            ),
        )

    async def stealth_disable(
        self, credentials: sending.SendingCredentials, chat_id: UUID,
    ) -> None:
        """Disable stealth mode

        Arguments:
            credentials: credentials of chat.
            chat_id: id of chat to disable stealth,
        """
        await self._obtain_token(credentials)
        return await self.client.stealth_disable(
            credentials=credentials,
            payload=StealthDisablePayload(group_chat_id=chat_id,),
        )

    async def add_users(
        self,
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
        await self._obtain_token(credentials)
        return await self.client.add_users(
            credentials=credentials,
            payload=AddRemoveUsersPayload(
                group_chat_id=chat_id, user_huids=users_huids
            ),
        )

    async def remove_users(
        self,
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
        await self._obtain_token(credentials)
        return await self.client.remove_users(
            credentials=credentials,
            payload=AddRemoveUsersPayload(
                group_chat_id=chat_id, user_huids=users_huids
            ),
        )

    async def _obtain_token(self, credentials: sending.SendingCredentials) -> None:
        """Get token for bot and fill credentials.

        Arguments:
            credentials: credentials that should be filled with token.
        """
        assert credentials.host, "host is required in credentials for obtaining token"
        assert (
            credentials.bot_id
        ), "bot_id is required in credentials for obtaining token"

        cts = self._get_cts_by_host(credentials.host)

        if cts.server_credentials and cts.server_credentials.token:
            credentials.token = cts.server_credentials.token
            return

        signature = cts.calculate_signature(credentials.bot_id)
        token = await self.client.obtain_token(
            credentials.host, credentials.bot_id, signature
        )
        cts.server_credentials = ServerCredentials(
            bot_id=credentials.bot_id, token=token
        )
        credentials.token = token
