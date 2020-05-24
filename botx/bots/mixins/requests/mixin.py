"""Definition for mixin that defines BotX API methods."""

from typing import TYPE_CHECKING, Optional, TypeVar

from botx.bots.mixins.requests import bots, chats, command, events, notification, users
from botx.clients.methods.base import BotXMethod
from botx.models import sending

if TYPE_CHECKING:
    from botx.bots.bot import Bot  # noqa: WPS433

ResponseT = TypeVar("ResponseT")


class BotXRequestsMixin(
    bots.BotsRequestsMixin,
    chats.ChatsRequestsMixin,
    command.CommandRequestsMixin,
    events.EventsRequestsMixin,
    notification.NotificationRequestsMixin,
    users.UsersRequestsMixin,
):
    """Mixin that defines methods for communicating with BotX API."""

    async def call_method(
        self: "Bot",
        method: BotXMethod[ResponseT],
        *,
        host: Optional[str] = None,
        token: Optional[str] = None,
        credentials: Optional[sending.SendingCredentials] = None,
    ) -> ResponseT:
        if host is not None and token is not None:
            method.configure(host=host, token=token)
        elif credentials is not None:
            method.configure(
                host=credentials.host, token=self.get_token_for_cts(credentials.host)
            )
        return await method.call(self.client)
