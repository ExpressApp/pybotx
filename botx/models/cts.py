import base64
import hashlib
import hmac
from typing import List, Optional
from uuid import UUID

from .base import BotXType


class CTSCredentials(BotXType):
    bot_id: UUID
    token: str


class CTS(BotXType):
    host: str
    secret_key: str
    credentials: Optional[CTSCredentials] = None

    def calculate_signature(self, bot_id: UUID) -> str:
        return base64.b16encode(
            hmac.new(
                key=self.secret_key.encode(),
                msg=str(bot_id).encode(),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode()


class BotCredentials(BotXType):
    known_cts: List[CTS] = []
