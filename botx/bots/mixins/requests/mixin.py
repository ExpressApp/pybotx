"""Definition for mixin that defines BotX API methods."""
from typing import Optional, TypeVar, cast
from uuid import UUID

from loguru import logger

from botx.bots.mixins.requests import (
    bots,
    chats,
    command,
    events,
    internal_bot_notification,
    notification,
    users,
)
from botx.clients.clients.async_client import AsyncClient
from botx.clients.methods.base import BotXMethod
from botx.models.credentials import BotXCredentials
from botx.models.messages.sending.credentials import SendingCredentials

ResponseT = TypeVar("ResponseT")

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # noqa: WPS433, WPS440, F401


class CredentialsSearchProtocol(Protocol):
    """Protocol for search token in local credentials."""

    def get_token_for_bot(self, bot_id: UUID) -> str:
        """Search token in local credentials."""

    def get_account_by_bot_id(self, bot_id: UUID) -> BotXCredentials:
        """Get bot credentials by bot id."""


# A lot of base classes since it's mixin for all shorthands for BotX API requests
class BotXRequestsMixin(  # noqa: WPS215
    bots.BotsRequestsMixin,
    chats.ChatsRequestsMixin,
    command.CommandRequestsMixin,
    events.EventsRequestsMixin,
    notification.NotificationRequestsMixin,
    users.UsersRequestsMixin,
    internal_bot_notification.InternalBotNotificationRequestsMixin,
):
    """Mixin that defines methods for communicating with BotX API."""

    client: AsyncClient

    # TODO: remove SendingCredential from client module.
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
        if credentials is not None:
            debug_bot_id = credentials.bot_id
            host = cast(str, credentials.host)
            bot_id = cast(UUID, credentials.bot_id)
            method.configure(
                host=host,
                token=cast(CredentialsSearchProtocol, self).get_token_for_bot(bot_id),
            )
        else:
            debug_bot_id = bot_id
            method.configure(host=host or method.host, token=token or method.token)

        request = self.client.build_request(method)

        logger.bind(botx_client=True, payload=request.dict()).debug(
            "send {0} request to bot {1}",
            method.__repr_name__(),  # noqa: WPS609
            debug_bot_id,
        )

        response = await self.client.execute(request)
        return await self.client.process_response(method, response)
