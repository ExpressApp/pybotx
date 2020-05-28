"""Mixin for shortcut for bots resource requests."""

from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v2.bots.token import Token


class BotsRequestsMixin:
    """Mixin for shortcut for bots resource requests."""

    async def get_token(
        self: BotXMethodCallProtocol, host: str, bot_id: UUID, signature: str,
    ) -> str:
        """Obtain token for bot.

        Arguments:
            host: host on which request should be made.
            bot_id: ID of bot for which token should be obtained.
            signature: calculated signature of bot.

        Returns:
             Obtained token.
        """
        return await self.call_method(
            Token(bot_id=bot_id, signature=signature), host=host,
        )
