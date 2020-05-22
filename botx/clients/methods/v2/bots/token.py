from typing import Dict
from uuid import UUID

from httpx import URL

from botx.clients.methods.base import BotXMethod


class Token(BotXMethod[str]):
    __url__ = "/api/v2/botx/bots/{bot_id}/token"
    __method__ = "GET"
    __returning__ = str

    bot_id: UUID
    signature: str

    @property
    def url(self) -> str:
        api_url = self.__url__.format(bot_id=self.bot_id)
        return str(URL(self.base_url).join(api_url))

    @property
    def params(self) -> Dict[str, str]:
        return {"signature": self.signature}

    def encode(self) -> None:
        return None
