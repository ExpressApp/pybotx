from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from time import monotonic
from uuid import UUID

from pybotx.domain.widgets import MultiWidgetState, SingleWidgetState
from pybotx.domain.ports.widget_state_store import WidgetStateStorePort


@dataclass(slots=True)
class _StoredItem:
    state: object
    expires_at: float | None


class WidgetStateSerializer:
    def dumps(self, state: object) -> bytes:  # pragma: no cover
        raise NotImplementedError

    def loads(self, payload: bytes) -> object:  # pragma: no cover
        raise NotImplementedError


class JsonWidgetStateSerializer(WidgetStateSerializer):
    def __init__(self, *, write_version: int = 2) -> None:
        if write_version not in {1, 2}:
            raise ValueError("write_version must be 1 or 2")
        self._write_version = write_version

    def dumps(self, state: object) -> bytes:
        return json.dumps(self._encode(state), separators=(",", ":")).encode("utf-8")

    def loads(self, payload: bytes) -> object:
        data = json.loads(payload.decode("utf-8"))
        return self._decode(data)

    def _encode(self, state: object) -> object:
        if isinstance(state, SingleWidgetState):
            if self._write_version == 1:
                return {
                    "__type__": "SingleWidgetState",
                    "__version__": 1,
                    "elems": state.elems,
                    "current_index": state.current_index,
                }
            return {
                "__type__": "SingleWidgetState",
                "__version__": 2,
                "items": state.elems,
                "index": state.current_index,
            }
        if isinstance(state, MultiWidgetState):
            if self._write_version == 1:
                return {
                    "__type__": "MultiWidgetState",
                    "__version__": 1,
                    "elems": state.elems,
                    "page": state.page,
                    "sync_ids": [str(sync_id) for sync_id in state.sync_ids],
                }
            return {
                "__type__": "MultiWidgetState",
                "__version__": 2,
                "items": state.elems,
                "page": state.page,
                "sync_ids": [str(sync_id) for sync_id in state.sync_ids],
            }
        if isinstance(state, UUID):
            return {
                "__type__": "UUID",
                "__version__": self._write_version,
                "value": str(state),
            }
        return state

    def _decode(self, data: object) -> object:
        if isinstance(data, dict) and "__type__" in data:
            marker = data.get("__type__")
            version = data.get("__version__")
            if version not in {1, 2}:
                raise ValueError("Unsupported widget state serializer version")
            if marker == "SingleWidgetState":
                if version == 1:
                    elems = data.get("elems")
                    current_index = data.get("current_index")
                else:
                    elems = data.get("items")
                    current_index = data.get("index")
                if not isinstance(elems, list):
                    raise ValueError("SingleWidgetState.elems must be a list")
                if isinstance(current_index, bool) or not isinstance(current_index, int):
                    raise ValueError("SingleWidgetState.current_index must be int")
                return SingleWidgetState(
                    elems=list(elems),
                    current_index=current_index,
                )
            if marker == "MultiWidgetState":
                if version == 1:
                    elems = data.get("elems")
                else:
                    elems = data.get("items")
                page = data.get("page")
                sync_ids = data.get("sync_ids")
                if not isinstance(elems, list):
                    raise ValueError("MultiWidgetState.elems must be a list")
                if isinstance(page, bool) or not isinstance(page, int):
                    raise ValueError("MultiWidgetState.page must be int")
                if not isinstance(sync_ids, list) or not all(
                    isinstance(item, str) for item in sync_ids
                ):
                    raise ValueError("MultiWidgetState.sync_ids must be list[str]")
                return MultiWidgetState(
                    elems=list(elems),
                    page=page,
                    sync_ids=[UUID(value) for value in sync_ids],
                )
            if marker == "UUID":
                value = data.get("value")
                if not isinstance(value, str):
                    raise ValueError("UUID.value must be string")
                return UUID(value)
        return data


class PickleWidgetStateSerializer(WidgetStateSerializer):
    def dumps(self, state: object) -> bytes:
        import pickle

        return pickle.dumps(state)

    def loads(self, payload: bytes) -> object:
        import pickle

        return pickle.loads(payload)


class InMemoryWidgetStateStore(WidgetStateStorePort):
    def __init__(self) -> None:
        self._items: dict[UUID, _StoredItem] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: UUID) -> object | None:
        async with self._lock:
            item = self._items.get(key)
            if item is None:
                return None
            if item.expires_at is not None and item.expires_at <= monotonic():
                self._items.pop(key, None)
                return None
            return item.state

    async def set(
        self,
        key: UUID,
        state: object,
        *,
        ttl_seconds: float | None = None,
    ) -> None:
        expires_at = None
        if ttl_seconds is not None:
            expires_at = monotonic() + ttl_seconds
        async with self._lock:
            self._items[key] = _StoredItem(state=state, expires_at=expires_at)

    async def delete(self, key: UUID) -> None:
        async with self._lock:
            self._items.pop(key, None)


class RedisWidgetStateStore(WidgetStateStorePort):
    def __init__(
        self,
        *,
        redis,
        prefix: str = "widget_state:",
        serializer: WidgetStateSerializer | None = None,
    ) -> None:
        self._redis = redis
        self._prefix = prefix
        self._serializer = serializer or JsonWidgetStateSerializer()

    def _key(self, key: UUID) -> str:
        return f"{self._prefix}{key}"

    async def get(self, key: UUID) -> object | None:
        raw = await self._redis.get(self._key(key))
        if raw is None:
            return None
        return self._serializer.loads(raw)

    async def set(
        self,
        key: UUID,
        state: object,
        *,
        ttl_seconds: float | None = None,
    ) -> None:
        payload = self._serializer.dumps(state)
        if ttl_seconds is None:
            await self._redis.set(self._key(key), payload)
        else:
            await self._redis.set(self._key(key), payload, ex=ttl_seconds)

    async def delete(self, key: UUID) -> None:
        await self._redis.delete(self._key(key))

__all__ = (
    "InMemoryWidgetStateStore",
    "RedisWidgetStateStore",
    "WidgetStateSerializer",
    "JsonWidgetStateSerializer",
    "PickleWidgetStateSerializer",
)
