from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol, runtime_checkable
from uuid import UUID

from pybotx.domain.auth import BotXAuthVersion
from pybotx.domain.models.bot_account import BotAccountWithSecret


@runtime_checkable
class BotAccountsStoragePort(Protocol):
    def get_bot_account(self, bot_id: UUID) -> BotAccountWithSecret: ...  # pragma: no cover

    def iter_bot_accounts(self) -> Iterator[BotAccountWithSecret]: ...  # pragma: no cover

    def get_auth_version(self) -> BotXAuthVersion: ...  # pragma: no cover

    def get_cts_url(self, bot_id: UUID) -> str: ...  # pragma: no cover

    def set_token(self, bot_id: UUID, token: str) -> None: ...  # pragma: no cover

    def get_token_or_none(self, bot_id: UUID) -> str | None: ...  # pragma: no cover

    def build_jwt_v2(self, bot_id: UUID) -> str: ...  # pragma: no cover

    def build_signature(self, bot_id: UUID) -> str: ...  # pragma: no cover

    def ensure_bot_id_exists(self, bot_id: UUID) -> None: ...  # pragma: no cover
