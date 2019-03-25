import base64
import hashlib
import hmac
from typing import Dict, Optional, Tuple
from uuid import UUID

from .base import BotXType


class CTS(BotXType):
    host: str
    secret_key: str

    def calculate_signature(self, bot_id: UUID) -> str:
        return base64.b16encode(
            hmac.new(
                key=self.secret_key.encode(),
                msg=str(bot_id).encode(),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode()


class CTSCredentials(BotXType):
    bot_id: UUID
    result: str


class BotCredentials(BotXType):
    known_cts: Dict[str, Tuple[CTS, Optional[CTSCredentials]]] = {}
