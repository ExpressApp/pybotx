"""Definition for mixin that defines BotX API methods."""

from typing import TYPE_CHECKING, List, Optional, Sequence, TypeVar, cast
from uuid import UUID

from botx import utils
from botx.clients.clients import AsyncClient
from botx.clients.methods.base import BotXMethod
from botx.clients.methods.v2.bots.token import Token
from botx.clients.methods.v3.chats.add_user import AddUser
from botx.clients.methods.v3.chats.remove_user import RemoveUser
from botx.clients.methods.v3.chats.stealth_disable import StealthDisable
from botx.clients.methods.v3.chats.stealth_set import StealthSet
from botx.clients.methods.v3.command.command_result import CommandResult
from botx.clients.methods.v3.events.edit_event import EditEvent, UpdatePayload
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.methods.v3.notification.notification import Notification
from botx.clients.types.options import ResultOptions
from botx.clients.types.result_payload import ResultPayload
from botx.models import sending

if TYPE_CHECKING:
    from botx.bots.bots import Bot  # noqa: WPS433

ResponseT = TypeVar("ResponseT")


class APIMixin:
    """Mixin that defines methods for communicating with BotX API."""

    client: AsyncClient

    async def call_method(
        self: "Bot",
        method: BotXMethod[ResponseT],
        *,
        host: Optional[str] = None,
        token: Optional[str] = None,
        credentials: Optional[sending.SendingCredentials] = None,
    ) -> ResponseT:
        if host is not None and token is not None:
            method.fill_credentials(host, token)
        elif credentials is not None:
            method.fill_credentials(
                credentials.host, self.get_token_for_cts(credentials.host)
            )
        return await method.call(self.client)

    async def get_token(self, host: str, bot_id: UUID, signature: str) -> str:
        return await self.call_method(  # noqa: S106
            Token(bot_id=bot_id, signature=signature), host=host, token="",
        )

    async def send_command_result(
        self: "Bot",
        credentials: sending.SendingCredentials,
        payload: sending.MessagePayload,
    ) -> UUID:
        return await self.call_method(
            CommandResult(
                bot_id=cast(UUID, credentials.bot_id),
                sync_id=cast(UUID, credentials.sync_id),
                event_sync_id=credentials.message_id,
                result=ResultPayload(
                    body=payload.text,
                    bubble=payload.markup.bubbles,
                    keyboard=payload.markup.keyboard,
                    mentions=payload.options.mentions,
                ),
                recipients=payload.options.recipients,
                file=payload.file,
                opts=ResultOptions(notification_opts=payload.options.notifications),
            ),
            credentials=credentials,
        )

    async def send_notification(
        self: "Bot",
        credentials: sending.SendingCredentials,
        payload: sending.MessagePayload,
        group_chat_ids: Optional[Sequence[UUID]] = None,
    ) -> None:
        if group_chat_ids is not None:
            chat_ids = utils.optional_sequence_to_list(group_chat_ids)
        else:
            chat_ids = [credentials.chat_id]

        return await self.call_method(
            Notification(
                bot_id=cast(UUID, credentials.bot_id),
                group_chat_ids=chat_ids,
                result=ResultPayload(
                    body=payload.text,
                    bubble=payload.markup.bubbles,
                    keyboard=payload.markup.keyboard,
                    mentions=payload.options.mentions,
                ),
                recipients=payload.options.recipients,
                file=payload.file,
                opts=ResultOptions(notification_opts=payload.options.notifications),
            ),
            credentials=credentials,
        )

    async def send_direct_notification(
        self: "Bot",
        credentials: sending.SendingCredentials,
        payload: sending.MessagePayload,
    ) -> UUID:
        return await self.call_method(
            NotificationDirect(
                bot_id=cast(UUID, credentials.bot_id),
                group_chat_id=credentials.chat_id,
                event_sync_id=credentials.message_id,
                result=ResultPayload(
                    body=payload.text,
                    bubble=payload.markup.bubbles,
                    keyboard=payload.markup.keyboard,
                    mentions=payload.options.mentions,
                ),
                recipients=payload.options.recipients,
                file=payload.file,
                opts=ResultOptions(notification_opts=payload.options.notifications),
            ),
            credentials=credentials,
        )

    async def update_message(
        self: "Bot",
        credentials: sending.SendingCredentials,
        update: sending.UpdatePayload,
    ) -> None:
        """Change message by it's event id.

        Arguments:
            credentials: credentials that are used for sending message. *sync_id* is
                required for credentials.
            update: update of message content.
        """
        return await self.call_method(
            EditEvent(
                sync_id=credentials.sync_id,
                result=UpdatePayload(
                    body=update.text,
                    keyboard=update.keyboard,
                    bubble=update.bubbles,
                    mentions=update.mentions,
                ),
            ),
            credentials=credentials,
        )

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
        self, credentials: sending.SendingCredentials, chat_id: UUID,
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
        return await self.call_method(
            AddUser(group_chat_id=chat_id, user_huids=users_huids),
            credentials=credentials,
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
        return await self.call_method(
            RemoveUser(group_chat_id=chat_id, user_huids=users_huids),
            credentials=credentials,
        )
