import base64
import hashlib
import hmac
from typing import Dict, List, Optional
from uuid import UUID

from botx.bot.models.credentials import BotCredentials


class CredentialsStorage:
    def __init__(self, credentials_list: List[BotCredentials]) -> None:
        self._credentials_list = credentials_list
        self._auth_tokens: Dict[UUID, str] = {}

    def get_host(self, bot_id: UUID) -> str:
        credentials = self._get_credentials(bot_id)
        return credentials.host

    def set_token(self, bot_id: UUID, token: str) -> None:
        self._auth_tokens[bot_id] = token

    def get_token_or_none(self, bot_id: UUID) -> Optional[str]:
        return self._auth_tokens.get(bot_id)

    def build_signature(self, bot_id: UUID) -> str:
        credentials = self._get_credentials(bot_id)

        signed_bot_id = hmac.new(
            key=credentials.secret_key.encode(),
            msg=str(credentials.bot_id).encode(),
            digestmod=hashlib.sha256,
        ).digest()

        return base64.b16encode(signed_bot_id).decode()

    def _get_credentials(self, bot_id: UUID) -> BotCredentials:
        for credentials in self._credentials_list:
            if credentials.bot_id == bot_id:
                return credentials

        raise ValueError(f"No credentials for bot_id `{bot_id}`")
        # TODO: raise UnknownBotError(bot_id)
