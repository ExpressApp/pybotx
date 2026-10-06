import base64
import hashlib
import hmac
from collections.abc import Iterator, Sequence
from uuid import UUID

from pybotx.auth import BotXAuthVersion, build_botx_jwt_v2
from pybotx.bot.bot_account_provider import (
    BotAccountProvider,
    StaticBotAccountProvider,
)
from pybotx.bot.contextvars import bot_account_key_var
from pybotx.client.http_config import (
    BotXRetryPolicy,
    BotXRetryRequestPolicy,
    BotXRetryStrategy,
    SafeBotXRetryRequestPolicy,
)
from pybotx.client.observability import BotXRequestObserver
from pybotx.models.bot_account import BotAccountKey, BotAccountWithSecret


class BotAccountsStorage:
    def __init__(
        self,
        bot_accounts: Sequence[BotAccountWithSecret] | None = None,
        *,
        account_provider: BotAccountProvider | None = None,
        auth_version: BotXAuthVersion = BotXAuthVersion.V2,
        retry_policy: BotXRetryPolicy | None = None,
        retry_request_policy: BotXRetryRequestPolicy | None = None,
        retry_strategy: BotXRetryStrategy | None = None,
        metrics_collector: BotXRequestObserver | None = None,
        tracing_collector: BotXRequestObserver | None = None,
    ) -> None:
        if bot_accounts is not None and account_provider is not None:
            raise ValueError(
                "Pass either `bot_accounts` or `account_provider`, not both"
            )
        self._account_provider = account_provider or StaticBotAccountProvider(
            bot_accounts or ()
        )
        self._auth_tokens: dict[tuple[BotAccountKey | UUID, int], str] = {}
        self._auth_version = auth_version
        self._retry_policy = retry_policy
        self._retry_request_policy = (
            retry_request_policy
            if retry_policy is not None
            else None
        )
        if retry_policy is not None and self._retry_request_policy is None:
            self._retry_request_policy = SafeBotXRetryRequestPolicy()
        self._retry_strategy = retry_strategy
        self._metrics_collector = metrics_collector
        self._tracing_collector = tracing_collector

    def get_bot_account(self, bot_id: UUID) -> BotAccountWithSecret:
        account_key = self._get_current_account_key(bot_id)
        if account_key is not None:
            return self._account_provider.get_account(account_key)
        return self._account_provider.get_account_by_bot_id(bot_id)

    def resolve_incoming_account_key(
        self,
        *,
        bot_id: UUID,
        host: str | None,
    ) -> BotAccountKey:
        return self._account_provider.resolve_incoming_account_key(
            bot_id=bot_id,
            host=host,
        )

    def ensure_account_key_exists(self, account_key: BotAccountKey) -> None:
        self._account_provider.get_account(account_key)

    def iter_bot_accounts(self) -> Iterator[BotAccountWithSecret]:
        yield from self._account_provider.iter_bot_accounts()

    def get_auth_version(self) -> BotXAuthVersion:
        return self._auth_version

    def get_retry_policy(self) -> BotXRetryPolicy | None:
        return self._retry_policy

    def get_retry_request_policy(self) -> BotXRetryRequestPolicy | None:
        return self._retry_request_policy

    def get_retry_strategy(self) -> BotXRetryStrategy | None:
        return self._retry_strategy

    def iter_request_observers(self) -> Iterator[BotXRequestObserver]:
        if self._metrics_collector is not None:
            yield self._metrics_collector
        if self._tracing_collector is not None:
            yield self._tracing_collector

    def get_cts_url(self, bot_id: UUID) -> str:
        bot_account = self.get_bot_account(bot_id)
        return str(bot_account.cts_url)

    def set_token(self, bot_id: UUID, token: str) -> None:
        self._auth_tokens[self._token_cache_key(bot_id)] = token

    def get_token_or_none(self, bot_id: UUID) -> str | None:
        return self._auth_tokens.get(self._token_cache_key(bot_id))

    def build_jwt_v2(self, bot_id: UUID) -> str:
        bot_account = self.get_bot_account(bot_id)
        return build_botx_jwt_v2(
            bot_id=bot_account.id,
            bot_host=bot_account.host,
            secret_key=bot_account.secret_key,
        )

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

    def invalidate(self, account_key: BotAccountKey) -> None:
        for cache_key in tuple(self._auth_tokens):
            if cache_key[0] == account_key:
                self._auth_tokens.pop(cache_key, None)

    def _token_cache_key(self, bot_id: UUID) -> tuple[BotAccountKey | UUID, int]:
        account = self.get_bot_account(bot_id)
        account_key = self._get_current_account_key(bot_id)
        return (account_key or account.account_key or account.id, account.revision)

    @staticmethod
    def _get_current_account_key(bot_id: UUID) -> BotAccountKey | None:
        try:
            account_key = bot_account_key_var.get()
        except LookupError:
            return None
        if account_key.bot_id == bot_id:
            return account_key
        return None
