from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID


@runtime_checkable
class WidgetStateStorePort(Protocol):
    async def get(self, key: UUID) -> object | None: ...  # pragma: no cover

    async def set(
        self,
        key: UUID,
        state: object,
        *,
        ttl_seconds: float | None = None,
    ) -> None: ...  # pragma: no cover

    async def delete(self, key: UUID) -> None: ...  # pragma: no cover
