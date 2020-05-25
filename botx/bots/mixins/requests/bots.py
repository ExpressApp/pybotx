"""Definition for mixin that defines BotX API methods."""

from uuid import UUID

from botx.bots.mixins.requests.mixin import BotXMethodCallProtocol
from botx.clients.methods.v2.bots.token import Token


class BotsRequestsMixin(BotXMethodCallProtocol):
    """Mixin that defines methods for communicating with BotX API."""

    async def get_token(self, host: str, bot_id: UUID, signature: str) -> str:
        return await self.call_method(  # noqa: S106
            Token(bot_id=bot_id, signature=signature), host=host,
        )
