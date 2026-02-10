from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from pybotx.application.handler import IncomingMessageHandlerFunc
from pybotx.domain.logger import logger
from pybotx.domain.models.message.incoming_message import IncomingMessage
from pybotx.domain.ports.dedup_store import DedupStorePort


DedupKeyBuilder = Callable[[IncomingMessage], str]


def _default_key_builder(message: IncomingMessage) -> str:
    bot_id: UUID = message.bot.id
    return f"{bot_id}:{message.sync_id}"


class DedupMiddleware:
    def __init__(
        self,
        *,
        store: DedupStorePort,
        ttl_seconds: float = 300.0,
        key_builder: DedupKeyBuilder | None = None,
        enabled: bool = True,
    ) -> None:
        self._store = store
        self._ttl_seconds = ttl_seconds
        self._key_builder = key_builder or _default_key_builder
        self._enabled = enabled

    async def dispatch(
        self,
        message: IncomingMessage,
        bot,  # Bot type omitted to avoid circular import
        call_next: IncomingMessageHandlerFunc,
    ) -> None:
        if not self._enabled:
            await call_next(message, bot)
            return

        try:
            key = self._key_builder(message)
            is_new = await self._store.mark_seen(key, self._ttl_seconds)
        except Exception:
            logger.exception("Deduplication store failure. Processing message anyway.")
            await call_next(message, bot)
            return

        if not is_new:
            logger.debug("Duplicate message skipped: {key}", key=key)
            return

        await call_next(message, bot)
