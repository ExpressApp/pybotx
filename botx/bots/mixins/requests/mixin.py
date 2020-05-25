"""Definition for mixin that defines BotX API methods."""
from typing import Any, Optional, Protocol, TypeVar, cast

from botx.bots.mixins.requests import bots, chats, command, events, notification, users
from botx.clients.client import AsyncClient
from botx.clients.methods.base import BotXMethod
from botx.models import sending

ResponseT = TypeVar("ResponseT")


class TokenSearchProtocol(Protocol):
    def get_token_for_cts(self, host: str) -> str:
        ...


class ClientOwnerProtocol(Protocol):
    @property
    def client(self) -> AsyncClient:
        ...


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

    async def call_method(
        self,
        method: BotXMethod[Any],
        *,
        host: Optional[str] = None,
        token: Optional[str] = None,
        credentials: Optional[sending.SendingCredentials] = None,
    ) -> Any:
        if credentials is not None:
            host = cast(str, credentials.host)
            method.configure(
                host=host, token=cast(TokenSearchProtocol, self).get_token_for_cts(host)
            )
        else:
            method.configure(host=host or method.host, token=token or method.token)

        return await method.call(cast(ClientOwnerProtocol, self).client)
