from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Protocol
from uuid import UUID

from pybotx.bot.exceptions import UnknownBotAccountError
from pybotx.models.bot_account import BotAccountKey, BotAccountWithSecret


class BotAccountProvider(Protocol):
    """Read-side port for resolving BotX credentials at runtime.

    Implementations must not perform blocking I/O. Dynamic providers should
    serve a locally cached snapshot and refresh it outside a request path.
    """

    def get_account(self, key: BotAccountKey) -> BotAccountWithSecret:
        """Return the credential for an explicit CTS and bot identity."""

    def get_account_by_bot_id(self, bot_id: UUID) -> BotAccountWithSecret:
        """Resolve only when ``bot_id`` is unambiguous for this provider."""

    def resolve_incoming_account_key(
        self,
        *,
        bot_id: UUID,
        host: str | None,
    ) -> BotAccountKey:
        """Map inbound Bot API identity to a stable account key."""

    def iter_bot_accounts(self) -> Iterator[BotAccountWithSecret]:
        """Yield known accounts for legacy startup token fetching."""


class StaticBotAccountProvider:
    """Backward-compatible adapter over the historical ``bot_accounts`` list."""

    def __init__(self, bot_accounts: Sequence[BotAccountWithSecret]) -> None:
        self._bot_accounts = tuple(bot_accounts)

    def get_account(self, key: BotAccountKey) -> BotAccountWithSecret:
        for account in self._bot_accounts:
            if account.id == key.bot_id:
                return account
        raise UnknownBotAccountError(key.bot_id)

    def get_account_by_bot_id(self, bot_id: UUID) -> BotAccountWithSecret:
        for account in self._bot_accounts:
            if account.id == bot_id:
                return account
        raise UnknownBotAccountError(bot_id)

    def resolve_incoming_account_key(
        self,
        *,
        bot_id: UUID,
        host: str | None,
    ) -> BotAccountKey:
        account = self.get_account_by_bot_id(bot_id)
        return BotAccountKey(server_id=host or account.host, bot_id=bot_id)

    def iter_bot_accounts(self) -> Iterator[BotAccountWithSecret]:
        yield from self._bot_accounts
