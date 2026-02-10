from uuid import UUID, uuid4

import pytest

from pybotx.domain.ports import WidgetStateStorePort
from pybotx.domain.widgets import MultiWidgetState, SingleWidgetState
from pybotx.infrastructure.widget_state_store import (
    InMemoryWidgetStateStore,
    JsonWidgetStateSerializer,
    PickleWidgetStateSerializer,
    RedisWidgetStateStore,
)


@pytest.mark.asyncio
async def test__widget_state_store__set_get_delete() -> None:
    store = InMemoryWidgetStateStore()
    key = uuid4()
    state = {"value": 1}

    await store.set(key, state, ttl_seconds=None)
    assert await store.get(key) == state

    await store.delete(key)
    assert await store.get(key) is None


def test__widget_state_store_port_importable() -> None:
    assert WidgetStateStorePort is not None


@pytest.mark.asyncio
async def test__widget_state_store__ttl_expiry(monkeypatch: pytest.MonkeyPatch) -> None:
    store = InMemoryWidgetStateStore()
    key = uuid4()
    state = {"value": 1}

    now = 100.0
    monkeypatch.setattr(
        "pybotx.infrastructure.widget_state_store.monotonic",
        lambda: now,
    )

    await store.set(key, state, ttl_seconds=5)
    assert await store.get(key) == state

    now = 200.0
    assert await store.get(key) is None


@pytest.mark.asyncio
async def test__redis_widget_state_store__set_get_delete() -> None:
    class DummyRedis:
        def __init__(self):
            self.storage = {}
            self.last_ex = None

        async def get(self, key):
            return self.storage.get(key)

        async def set(self, key, value, ex=None):
            self.storage[key] = value
            self.last_ex = ex

        async def delete(self, key):
            self.storage.pop(key, None)

    redis = DummyRedis()
    store = RedisWidgetStateStore(redis=redis, prefix="test:")
    key = uuid4()
    state = {"value": 1}

    await store.set(key, state)
    assert await store.get(key) == state

    await store.delete(key)
    assert await store.get(key) is None

    await store.set(key, state, ttl_seconds=10)
    assert redis.last_ex == 10


@pytest.mark.asyncio
async def test__redis_widget_state_store__json_serializer_roundtrip() -> None:
    class DummyRedis:
        def __init__(self):
            self.storage = {}

        async def get(self, key):
            return self.storage.get(key)

        async def set(self, key, value, ex=None):
            self.storage[key] = value

        async def delete(self, key):
            self.storage.pop(key, None)

    redis = DummyRedis()
    store = RedisWidgetStateStore(
        redis=redis,
        prefix="test:",
        serializer=JsonWidgetStateSerializer(),
    )
    key = uuid4()
    single_state = SingleWidgetState(elems=["a", "b"], current_index=1)

    await store.set(key, single_state)
    result = await store.get(key)
    assert isinstance(result, SingleWidgetState)
    assert result == single_state

    key_multi = uuid4()
    multi_state = MultiWidgetState(
        elems=[1, 2, 3],
        page=2,
        sync_ids=[uuid4(), uuid4()],
    )
    await store.set(key_multi, multi_state)
    result_multi = await store.get(key_multi)
    assert isinstance(result_multi, MultiWidgetState)
    assert result_multi == multi_state


def test__json_widget_state_serializer__uuid_roundtrip() -> None:
    serializer = JsonWidgetStateSerializer()
    value = uuid4()
    payload = serializer.dumps(value)
    restored = serializer.loads(payload)
    assert restored == value


def test__json_widget_state_serializer__write_version_1() -> None:
    serializer = JsonWidgetStateSerializer(write_version=1)
    payload = serializer.dumps(SingleWidgetState(elems=["x"], current_index=0))
    assert b'"__version__":1' in payload
    assert b'"elems"' in payload
    assert b'"current_index"' in payload

    payload_multi = serializer.dumps(
        MultiWidgetState(elems=[1], page=0, sync_ids=[UUID("00000000-0000-0000-0000-000000000000")]),
    )
    assert b'"__version__":1' in payload_multi
    assert b'"elems"' in payload_multi


def test__json_widget_state_serializer__invalid_write_version() -> None:
    with pytest.raises(ValueError, match="write_version must be 1 or 2"):
        JsonWidgetStateSerializer(write_version=3)


def test__pickle_widget_state_serializer__roundtrip() -> None:
    serializer = PickleWidgetStateSerializer()
    payload = serializer.dumps({"value": 42})
    restored = serializer.loads(payload)
    assert restored == {"value": 42}


def test__json_widget_state_serializer__version_checks() -> None:
    serializer = JsonWidgetStateSerializer()
    payload_v1 = b'{"__type__":"Unknown","__version__":1,"value":"x"}'
    payload_v2 = b'{"__type__":"Unknown","__version__":2,"value":"x"}'
    assert serializer.loads(payload_v1) == {"__type__": "Unknown", "__version__": 1, "value": "x"}
    assert serializer.loads(payload_v2) == {"__type__": "Unknown", "__version__": 2, "value": "x"}
    with pytest.raises(ValueError, match="Unsupported widget state serializer version"):
        serializer.loads(payload_v1.replace(b"__version__\":1", b"__version__\":3"))
    with pytest.raises(ValueError, match="Unsupported widget state serializer version"):
        serializer.loads(b'{"__type__":"Unknown","value":"x"}')


def test__json_widget_state_serializer__invalid_schema() -> None:
    serializer = JsonWidgetStateSerializer()
    with pytest.raises(ValueError, match="SingleWidgetState.elems must be a list"):
        serializer.loads(
            b'{"__type__":"SingleWidgetState","__version__":2,"items":"bad","index":1}',
        )
    with pytest.raises(ValueError, match="SingleWidgetState.current_index must be int"):
        serializer.loads(
            b'{"__type__":"SingleWidgetState","__version__":2,"items":[],"index":"1"}',
        )
    with pytest.raises(ValueError, match="MultiWidgetState.sync_ids must be list\\[str\\]"):
        serializer.loads(
            b'{"__type__":"MultiWidgetState","__version__":2,"items":[],"page":0,"sync_ids":[1]}',
        )
    with pytest.raises(ValueError, match="MultiWidgetState.elems must be a list"):
        serializer.loads(
            b'{"__type__":"MultiWidgetState","__version__":2,"items":"bad","page":0,"sync_ids":[]}',
        )
    with pytest.raises(ValueError, match="MultiWidgetState.page must be int"):
        serializer.loads(
            b'{"__type__":"MultiWidgetState","__version__":2,"items":[],"page":"1","sync_ids":[]}',
        )
    with pytest.raises(ValueError, match="UUID.value must be string"):
        serializer.loads(b'{"__type__":"UUID","__version__":2,"value":1}')


def test__json_widget_state_serializer__v1_migration() -> None:
    serializer = JsonWidgetStateSerializer()
    payload = b'{"__type__":"SingleWidgetState","__version__":1,"elems":["a"],"current_index":1}'
    restored = serializer.loads(payload)
    assert restored == SingleWidgetState(elems=["a"], current_index=1)

    payload_multi = (
        b'{"__type__":"MultiWidgetState","__version__":1,'
        b'"elems":[1,2],"page":1,"sync_ids":["00000000-0000-0000-0000-000000000000"]}'
    )
    restored_multi = serializer.loads(payload_multi)
    assert restored_multi == MultiWidgetState(
        elems=[1, 2],
        page=1,
        sync_ids=[UUID("00000000-0000-0000-0000-000000000000")],
    )
