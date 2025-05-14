import base64
import hashlib
import hmac
from typing import Dict, Iterator, List, Optional
from uuid import UUID

from pybotx.bot.exceptions import UnknownBotAccountError
from pybotx.models.bot_account import BotAccountWithSecret


class BotAccountsStorage:
    def __init__(self, bot_accounts: List[BotAccountWithSecret]) -> None:
        self._bot_accounts = bot_accounts
        self._auth_tokens: Dict[UUID, str] = {}

    def get_bot_account(self, bot_id: UUID) -> BotAccountWithSecret:
        for bot_account in self._bot_accounts:
            if bot_account.id == bot_id:
                return bot_account

        raise UnknownBotAccountError(bot_id)

    def iter_bot_accounts(self) -> Iterator[BotAccountWithSecret]:
        yield from self._bot_accounts

    def get_cts_url(self, bot_id: UUID) -> str:
        bot_account = self.get_bot_account(bot_id)
        return bot_account.cts_url

    def set_token(self, bot_id: UUID, token: str) -> None:
        self._auth_tokens[bot_id] = token

    def get_token_or_none(self, bot_id: UUID) -> Optional[str]:
        return self._auth_tokens.get(bot_id)

    def build_signature(self, bot_id: UUID) -> str:
        bot_account = self.get_bot_account(bot_id)

        signed_bot_id = hmac.new(
            key=bot_account.secret_key.encode(),
            msg=str(bot_account.id).encode(),
            digestmod=hashlib.sha256,
        ).digest()

        return base64.b16encode(signed_bot_id).decode()

    def ensure_bot_id_exists(self, bot_id: UUID) -> None:
        self.get_bot_account(bot_id)
