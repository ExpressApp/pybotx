"""Definition for mixin that defines BotX API methods."""

from typing import TYPE_CHECKING
from uuid import UUID

from botx.clients.methods.v2.bots.token import Token

if TYPE_CHECKING:
    from botx.bots.bot import Bot  # noqa: WPS433


class BotsRequestsMixin:
    """Mixin that defines methods for communicating with BotX API."""

    async def get_token(self: "Bot", host: str, bot_id: UUID, signature: str) -> str:
        return await self.call_method(  # noqa: S106
            Token(bot_id=bot_id, signature=signature), host=host, token="",
        )
