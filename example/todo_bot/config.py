from __future__ import annotations

import os
from dataclasses import dataclass
from uuid import UUID

from pybotx import BotXAuthVersion


@dataclass(frozen=True)
class Settings:
    bot_id: UUID
    bot_secret: str
    cts_url: str
    auth_version: BotXAuthVersion
    verify_requests: bool
    http_backend: str
    http_timeout: float
    use_raw_http_client: bool
    retry_enabled: bool
    retry_backend: str
    retry_stream: bool
    retry_max_attempts: int
    retry_min_delay: float
    retry_max_delay: float
    retry_multiplier: float
    retry_jitter: bool
    storage_backend: str
    dedup_enabled: bool
    dedup_ttl: float
    dedup_backend: str
    widget_state_backend: str
    widget_state_redis_url: str
    widget_state_redis_prefix: str
    widget_state_serializer: str
    widget_state_serializer_version: int
    widget_include_state_in_metadata: bool
    demo_enabled: bool
    demo_allow_risky: bool


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def _require_uuid_env(name: str) -> UUID:
    value = _require_env(name)
    try:
        return UUID(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a valid UUID") from exc


def _parse_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(f"{name} must be a boolean value (true/false)")


def _parse_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc


def _parse_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a float") from exc


def _parse_auth_version() -> BotXAuthVersion:
    raw = os.getenv("BOT_AUTH_VERSION", BotXAuthVersion.V2.value)
    normalized = raw.strip().lower()
    if normalized == BotXAuthVersion.V1.value:
        return BotXAuthVersion.V1
    if normalized == BotXAuthVersion.V2.value:
        return BotXAuthVersion.V2
    raise RuntimeError("BOT_AUTH_VERSION must be 'v1' or 'v2'")


def _parse_http_backend() -> str:
    backend = os.getenv("HTTP_BACKEND", "httpx").strip().lower()
    if backend not in {"httpx", "aiohttp"}:
        raise RuntimeError("HTTP_BACKEND must be 'httpx' or 'aiohttp'")
    return backend


def _parse_http_timeout() -> float:
    return _parse_float("HTTP_TIMEOUT", 60.0)


def _parse_use_raw_http_client() -> bool:
    return _parse_bool("USE_RAW_HTTP_CLIENT", False)


def _parse_retry_backend() -> str:
    backend = os.getenv("HTTP_RETRY_BACKEND", "noop").strip().lower()
    if backend not in {"noop", "tenacity"}:
        raise RuntimeError("HTTP_RETRY_BACKEND must be 'noop' or 'tenacity'")
    return backend


def _parse_storage_backend() -> str:
    backend = os.getenv("TODO_STORAGE", "memory").strip().lower()
    if backend != "memory":
        raise RuntimeError("TODO_STORAGE must be 'memory'")
    return backend


def _parse_dedup_backend() -> str:
    backend = os.getenv("BOT_DEDUP_BACKEND", "memory").strip().lower()
    if backend not in {"memory", "noop"}:
        raise RuntimeError("BOT_DEDUP_BACKEND must be 'memory' or 'noop'")
    return backend


def _parse_widget_state_backend() -> str:
    backend = os.getenv("WIDGET_STATE_BACKEND", "memory").strip().lower()
    if backend not in {"memory", "redis"}:
        raise RuntimeError("WIDGET_STATE_BACKEND must be 'memory' or 'redis'")
    return backend


def _parse_widget_state_redis_url() -> str:
    return os.getenv("WIDGET_STATE_REDIS_URL", "redis://localhost:6379/0")


def _parse_widget_state_redis_prefix() -> str:
    return os.getenv("WIDGET_STATE_REDIS_PREFIX", "todo_widget:")


def _parse_widget_state_serializer() -> str:
    serializer = os.getenv("WIDGET_STATE_SERIALIZER", "json").strip().lower()
    if serializer not in {"json", "pickle"}:
        raise RuntimeError("WIDGET_STATE_SERIALIZER must be 'json' or 'pickle'")
    return serializer


def _parse_widget_state_serializer_version() -> int:
    return _parse_int("WIDGET_STATE_SERIALIZER_VERSION", 2)


def load_settings() -> Settings:
    return Settings(
        # bot_secret=_require_env("BOT_SECRET"),
        # bot_id=_require_uuid_env("BOT_ID"),
        bot_id=UUID("967687d6-9fd6-5771-8eee-a8b4c2460fd4"),
        bot_secret="da447cc4c6be940be1a549b40c2fc6e7",
        cts_url=os.getenv("CTS_URL", "https://cts1dev.ccsteam.ru"),
        auth_version=_parse_auth_version(),
        verify_requests=_parse_bool("VERIFY_REQUESTS", True),
        http_backend=_parse_http_backend(),
        http_timeout=_parse_http_timeout(),
        use_raw_http_client=_parse_use_raw_http_client(),
        retry_enabled=_parse_bool("HTTP_RETRY_ENABLED", False),
        retry_backend=_parse_retry_backend(),
        retry_stream=_parse_bool("HTTP_RETRY_STREAM", True),
        retry_max_attempts=_parse_int("HTTP_RETRY_MAX_ATTEMPTS", 3),
        retry_min_delay=_parse_float("HTTP_RETRY_MIN_DELAY", 0.1),
        retry_max_delay=_parse_float("HTTP_RETRY_MAX_DELAY", 2.0),
        retry_multiplier=_parse_float("HTTP_RETRY_MULTIPLIER", 2.0),
        retry_jitter=_parse_bool("HTTP_RETRY_JITTER", True),
        storage_backend=_parse_storage_backend(),
        dedup_enabled=_parse_bool("BOT_DEDUP_ENABLED", False),
        dedup_ttl=_parse_float("BOT_DEDUP_TTL", 300.0),
        dedup_backend=_parse_dedup_backend(),
        widget_state_backend=_parse_widget_state_backend(),
        widget_state_redis_url=_parse_widget_state_redis_url(),
        widget_state_redis_prefix=_parse_widget_state_redis_prefix(),
        widget_state_serializer=_parse_widget_state_serializer(),
        widget_state_serializer_version=_parse_widget_state_serializer_version(),
        widget_include_state_in_metadata=_parse_bool("WIDGET_INCLUDE_STATE_IN_METADATA", False),
        demo_enabled=_parse_bool("TODO_DEMO_ENABLED", True),
        demo_allow_risky=_parse_bool("TODO_DEMO_ALLOW_RISKY", True),
    )
