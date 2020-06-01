"""Definition for mixin that defines BotX API methods."""
from typing import Optional, TypeVar, cast

from botx.bots.mixins.requests import bots, chats, command, events, notification, users
from botx.clients.clients.async_client import AsyncClient
from botx.clients.methods.base import BotXMethod
from botx.models.messages.sending.credentials import SendingCredentials

ResponseT = TypeVar("ResponseT")

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import (  # type: ignore  # noqa: WPS433, WPS440, F401
        Protocol,
    )


class TokenSearchProtocol(Protocol):
    """Protocol for search token in local credentials."""

    def get_token_for_cts(self, host: str) -> str:
        """Search token in local credentials."""


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

    async def call_method(
        self,
        method: BotXMethod[ResponseT],
        *,
        host: Optional[str] = None,
        token: Optional[str] = None,
        credentials: Optional[SendingCredentials] = None,
    ) -> ResponseT:
        """Call method with async client.

        Arguments:
            method: method that should be user for request.
            host: host where request should be sent.
            token: token for method.
            credentials: credentials for making request.

        Returns:
            Response for method.
        """
        if credentials is not None:
            host = cast(str, credentials.host)
            method.configure(
                host=host,
                token=cast(TokenSearchProtocol, self).get_token_for_cts(host),
            )
        else:
            method.configure(host=host or method.host, token=token or method.token)

        return await self.client.call(method)
