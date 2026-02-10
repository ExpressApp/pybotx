import pytest

from pybotx.application.middlewares.dedup_middleware import DedupMiddleware
from pybotx.infrastructure.dedup_store import InMemoryDedupStore, NoopDedupStore


@pytest.mark.asyncio
async def test__inmemory_dedup_store__ttl_and_purge(monkeypatch: pytest.MonkeyPatch) -> None:
    from pybotx.infrastructure import dedup_store as dedup_module

    now = 0.0

    def _fake_monotonic():
        return now

    monkeypatch.setattr(dedup_module.time, "monotonic", _fake_monotonic)

    store = InMemoryDedupStore()

    assert await store.mark_seen("a", ttl_seconds=0.0) is True
    assert store._items == {}

    now = 1.0
    assert await store.mark_seen("a", ttl_seconds=10.0) is True
    assert await store.mark_seen("a", ttl_seconds=10.0) is False

    now = 20.0
    assert await store.mark_seen("a", ttl_seconds=10.0) is True


@pytest.mark.asyncio
async def test__noop_dedup_store__always_new() -> None:
    store = NoopDedupStore()

    assert await store.mark_seen("a", ttl_seconds=1.0) is True
    assert await store.mark_seen("a", ttl_seconds=1.0) is True


class _DummyStore:
    def __init__(self, *, result: bool = True, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.calls = []

    async def mark_seen(self, key: str, ttl_seconds: float) -> bool:
        self.calls.append((key, ttl_seconds))
        if self.error is not None:
            raise self.error
        return self.result


@pytest.mark.asyncio
async def test__dedup_middleware__disabled(incoming_message_factory) -> None:
    store = _DummyStore()
    middleware = DedupMiddleware(store=store, enabled=False)
    called = []

    async def _call_next(message, bot):  # type: ignore[no-untyped-def]
        called.append(message)

    message = incoming_message_factory()
    await middleware.dispatch(message, None, _call_next)

    assert called == [message]
    assert store.calls == []


@pytest.mark.asyncio
async def test__dedup_middleware__uses_default_key_builder(
    incoming_message_factory,
) -> None:
    store = _DummyStore(result=True)
    middleware = DedupMiddleware(store=store, ttl_seconds=123.0)
    called = []

    async def _call_next(message, bot):  # type: ignore[no-untyped-def]
        called.append(message)

    message = incoming_message_factory()
    await middleware.dispatch(message, None, _call_next)

    assert called == [message]
    assert store.calls == [(f"{message.bot.id}:{message.sync_id}", 123.0)]


@pytest.mark.asyncio
async def test__dedup_middleware__skips_duplicates(incoming_message_factory) -> None:
    store = _DummyStore(result=False)
    middleware = DedupMiddleware(store=store)
    called = []

    async def _call_next(message, bot):  # type: ignore[no-untyped-def]
        called.append(message)

    message = incoming_message_factory()
    await middleware.dispatch(message, None, _call_next)

    assert called == []


@pytest.mark.asyncio
async def test__dedup_middleware__store_failure_allows_processing(
    incoming_message_factory,
) -> None:
    store = _DummyStore(error=RuntimeError("boom"))
    middleware = DedupMiddleware(store=store)
    called = []

    async def _call_next(message, bot):  # type: ignore[no-untyped-def]
        called.append(message)

    message = incoming_message_factory()
    await middleware.dispatch(message, None, _call_next)

    assert called == [message]
