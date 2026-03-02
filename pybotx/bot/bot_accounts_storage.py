import base64
import hashlib
import hmac
from collections.abc import Iterator
from uuid import UUID

from pybotx.auth import BotXAuthVersion, build_botx_jwt_v2
from pybotx.bot.exceptions import UnknownBotAccountError
from pybotx.client.http_config import (
    BotXRetryPolicy,
    BotXRetryRequestPolicy,
    BotXRetryStrategy,
    SafeBotXRetryRequestPolicy,
)
from pybotx.client.observability import BotXRequestObserver
from pybotx.models.bot_account import BotAccountWithSecret


class BotAccountsStorage:
    def __init__(
        self,
        bot_accounts: list[BotAccountWithSecret],
        auth_version: BotXAuthVersion = BotXAuthVersion.V2,
        retry_policy: BotXRetryPolicy | None = None,
        retry_request_policy: BotXRetryRequestPolicy | None = None,
        retry_strategy: BotXRetryStrategy | None = None,
        metrics_collector: BotXRequestObserver | None = None,
        tracing_collector: BotXRequestObserver | None = None,
    ) -> None:
        self._bot_accounts = bot_accounts
        self._auth_tokens: dict[UUID, str] = {}
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
        for bot_account in self._bot_accounts:
            if bot_account.id == bot_id:
                return bot_account

        raise UnknownBotAccountError(bot_id)

    def iter_bot_accounts(self) -> Iterator[BotAccountWithSecret]:
        yield from self._bot_accounts

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
        self._auth_tokens[bot_id] = token

    def get_token_or_none(self, bot_id: UUID) -> str | None:
        return self._auth_tokens.get(bot_id)

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
