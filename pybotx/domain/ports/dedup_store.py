from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class DedupStorePort(Protocol):
    async def mark_seen(self, key: str, ttl_seconds: float) -> bool: ...  # pragma: no cover
