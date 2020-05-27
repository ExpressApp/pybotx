"""Definition for mixin that defines BotX API methods."""

from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v2.bots.token import Token


class BotsRequestsMixin:
    """Mixin that defines methods for communicating with BotX API."""

    async def get_token(
        self: BotXMethodCallProtocol, host: str, bot_id: UUID, signature: str
    ) -> str:
        return await self.call_method(
            Token(bot_id=bot_id, signature=signature), host=host,
        )
