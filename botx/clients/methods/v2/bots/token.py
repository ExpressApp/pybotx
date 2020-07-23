"""Method for retrieving token for bot."""
from typing import Dict
from uuid import UUID

from httpx import URL

from botx.clients.methods.base import BotXMethod, PrimitiveDataType


class Token(BotXMethod[str]):
    """Method for retrieving token for bot."""

    __url__ = "/api/v2/botx/bots/{bot_id}/token"
    __method__ = "GET"
    __returning__ = str

    #: ID of bot which access for token.
    bot_id: UUID

    #: calculated signature from secret_key for bot.
    signature: str

    @property
    def url(self) -> str:
        """Full URL for request with filling bot_id."""
        super_url = URL(super().url)
        api_url = self.__url__.format(bot_id=self.bot_id)
        return str(super_url.join(api_url))

    @property
    def query_params(self) -> Dict[str, PrimitiveDataType]:
        """Query string query_params for request with signature key."""
        return {"signature": self.signature}

    def encode(self) -> None:
        """Return nothing to override request body.

        Returns:
            Nothing.
        """
        return None  # noqa: WPS324
