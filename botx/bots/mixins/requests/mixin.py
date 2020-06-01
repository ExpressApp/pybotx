"""Definition for mixin that defines BotX API methods."""
from typing import Optional, TypeVar, cast
from uuid import UUID

from botx.bots.mixins.requests import bots, chats, command, events, notification, users
from botx.clients.clients.async_client import AsyncClient
from botx.clients.methods.base import BotXMethod
from botx.clients.methods.v2.bots.token import Token
from botx.models.credentials import ExpressServer, ServerCredentials
from botx.models.messages.sending.credentials import SendingCredentials

ResponseT = TypeVar("ResponseT")

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import (  # type: ignore  # noqa: WPS433, WPS440, F401
        Protocol,
    )


class CredentialsSearchProtocol(Protocol):
    """Protocol for search token in local credentials."""

    def get_token_for_cts(self, host: str) -> str:
        """Search token in local credentials."""

    def get_cts_by_host(self, host: str) -> ExpressServer:
        """Get CTS by host."""


# A lot of base classes since it's mixin for all shorthands for BotX API requests
class BotXRequestsMixin(  # noqa: WPS215
    bots.BotsRequestsMixin,
    chats.ChatsRequestsMixin,
    command.CommandRequestsMixin,
    events.EventsRequestsMixin,
    notification.NotificationRequestsMixin,
    users.UsersRequestsMixin,
):
    """Mixin that defines methods for communicating with BotX API."""

    client: AsyncClient

    async def call_method(  # noqa: WPS211
        self,
        method: BotXMethod[ResponseT],
        *,
        host: Optional[str] = None,
        token: Optional[str] = None,
        bot_id: Optional[UUID] = None,
        credentials: Optional[SendingCredentials] = None,
    ) -> ResponseT:
        """Call method with async client.

        Arguments:
            method: method that should be user for request.
            host: host where request should be sent.
            token: token for method.
            bot_id: ID of bot that send request.
            credentials: credentials for making request.

        Returns:
            Response for method.
        """
        if not isinstance(method, Token):
            host = cast(str, credentials.host if credentials else host)
            await _fill_token(
                self.client,
                host,
                cast(UUID, credentials.bot_id if credentials else bot_id),
                cast(CredentialsSearchProtocol, self).get_cts_by_host(host),
            )

        if credentials is not None:
            host = cast(str, credentials.host)
            method.configure(
                host=host,
                token=cast(CredentialsSearchProtocol, self).get_token_for_cts(host),
            )
        else:
            method.configure(host=host or method.host, token=token or method.token)

        return await self.client.call(method)


async def _fill_token(
    client: AsyncClient, host: str, bot_id: UUID, server: ExpressServer,
) -> None:
    if server.server_credentials is not None:
        return

    method = Token(bot_id=bot_id, signature=server.calculate_signature(bot_id))
    server.server_credentials = ServerCredentials(
        bot_id=bot_id, token=await client.call(method, host),
    )
