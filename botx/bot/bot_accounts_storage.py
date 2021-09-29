import base64
import hashlib
import hmac
from typing import Dict, List, Optional
from uuid import UUID

from botx.bot.models.bot_account import BotAccount


class BotAccountsStorage:
    def __init__(self, bot_accounts: List[BotAccount]) -> None:
        self._bot_accounts = bot_accounts
        self._auth_tokens: Dict[UUID, str] = {}

    def get_host(self, bot_id: UUID) -> str:
        bot_account = self._get_bot_account(bot_id)
        return bot_account.host

    def set_token(self, bot_id: UUID, token: str) -> None:
        self._auth_tokens[bot_id] = token

    def get_token_or_none(self, bot_id: UUID) -> Optional[str]:
        return self._auth_tokens.get(bot_id)

    def build_signature(self, bot_id: UUID) -> str:
        bot_account = self._get_bot_account(bot_id)

        signed_bot_id = hmac.new(
            key=bot_account.secret_key.encode(),
            msg=str(bot_account.bot_id).encode(),
            digestmod=hashlib.sha256,
        ).digest()

        return base64.b16encode(signed_bot_id).decode()

    def _get_bot_account(self, bot_id: UUID) -> BotAccount:
        for bot_account in self._bot_accounts:
            if bot_account.bot_id == bot_id:
                return bot_account

        raise ValueError(f"No Bot account with bot_id `{bot_id}`")
        # TODO: raise UnknownBotError(bot_id)