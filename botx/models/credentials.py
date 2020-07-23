"""Definition of credentials that are used for access to BotX API."""

import base64
import hashlib
import hmac
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ServerCredentials(BaseModel):
    """Container for credentials for bot."""

    #: bot that retrieved token from API.
    bot_id: UUID

    #: token generated for bot.
    token: str


class ExpressServer(BaseModel):
    """Server on which bot can answer."""

    #: host name of server.
    host: str

    #: secret that will be used for generating signature for bot.
    secret_key: str

    #: obtained credentials for bot.
    server_credentials: Optional[ServerCredentials] = None

    def calculate_signature(self, bot_id: UUID) -> str:
        """Calculate signature for obtaining token for bot from BotX API.

        Arguments:
            bot_id: bot for which token should be generated.

        Returns:
            Calculated signature.
        """
        return base64.b16encode(
            hmac.new(
                key=self.secret_key.encode(),
                msg=str(bot_id).encode(),
                digestmod=hashlib.sha256,
            ).digest(),
        ).decode()
