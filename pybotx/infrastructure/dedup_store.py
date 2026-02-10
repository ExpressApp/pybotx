from __future__ import annotations

import asyncio
import time

from pybotx.domain.ports.dedup_store import DedupStorePort


class InMemoryDedupStore(DedupStorePort):
    def __init__(self) -> None:
        self._items: dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def mark_seen(self, key: str, ttl_seconds: float) -> bool:
        now = time.monotonic()
        expires_at = now + max(ttl_seconds, 0.0)
        async with self._lock:
            last_expiry = self._items.get(key)
            if last_expiry is not None and last_expiry > now:
                return False
            self._items[key] = expires_at
            self._purge_expired(now)
            return True

    def _purge_expired(self, now: float) -> None:
        expired = [key for key, expiry in self._items.items() if expiry <= now]
        for key in expired:
            self._items.pop(key, None)


class NoopDedupStore(DedupStorePort):
    async def mark_seen(self, key: str, ttl_seconds: float) -> bool:
        return True
