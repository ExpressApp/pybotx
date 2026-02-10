import asyncio
import sys
import types

import pytest

from pybotx import build_bot
from pybotx.application.handler_collector import HandlerCollector
from pybotx.container import BotXContainer, build_default_config, _merge_middlewares
from pybotx.domain.logger import get_logger, set_logger, setup_logger
from pybotx.infrastructure.aiohttp_client import AioHttpClientAdapter
from pybotx.infrastructure.retrying_http_client import RetryingHttpClient
from pybotx.infrastructure.widget_state_store import InMemoryWidgetStateStore
from pybotx.application.middlewares.dedup_middleware import DedupMiddleware


def test__build_bot__custom_jwt_encoder_override(bot_account) -> None:
    class DummyJwtEncoder:
        def encode(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return "token"

    dummy_encoder = DummyJwtEncoder()
    bot = build_bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        jwt_encoder=dummy_encoder,
    )

    assert bot._bot_accounts_storage._jwt_encoder is dummy_encoder


def test__build_bot__custom_jwt_verifier_override(bot_account) -> None:
    class DummyJwtVerifier:
        def decode(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return {}

    dummy_verifier = DummyJwtVerifier()
    bot = build_bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        jwt_verifier=dummy_verifier,
    )

    assert bot._request_verifier._jwt_verifier is dummy_verifier


def test__build_bot__logger_override(bot_account) -> None:
    class DummyLogger:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []

        def add(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            self.calls.append(("add", ""))
            return 1

        def remove(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            self.calls.append(("remove", ""))

        def debug(self, message: str, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            self.calls.append(("debug", message))

        def info(self, message: str, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            self.calls.append(("info", message))

        def warning(self, message: str, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            self.calls.append(("warning", message))

        def error(self, message: str, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            self.calls.append(("error", message))

        def exception(self, message: str, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            self.calls.append(("exception", message))

        def opt(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return self

        def enable(self, name: str) -> None:
            self.calls.append(("enable", name))

        def disable(self, name: str) -> None:
            self.calls.append(("disable", name))

    dummy_logger = DummyLogger()
    build_bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        logger=dummy_logger,
    )

    get_logger().debug("hello")

    assert ("debug", "hello") in dummy_logger.calls

    set_logger(setup_logger())


def test__build_bot__custom_request_verifier_override(bot_account) -> None:
    class DummyRequestVerifier:
        def verify(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            return None

    dummy_verifier = DummyRequestVerifier()
    bot = build_bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        request_verifier=dummy_verifier,
    )

    assert bot._request_verifier is dummy_verifier


def test__build_bot__custom_http_client_override(bot_account) -> None:
    dummy_client = object()

    bot = build_bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        http_client=dummy_client,
    )

    assert bot._botx_api.get_http_client() is dummy_client


def test__build_bot__custom_raw_http_client_override(bot_account) -> None:
    dummy_client = object()

    bot = build_bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        raw_http_client=dummy_client,
    )

    http_client = bot._botx_api.get_http_client()
    assert isinstance(http_client, RetryingHttpClient)
    assert http_client._client is dummy_client


def test__build_bot__retry_backend_override(bot_account) -> None:
    bot = build_bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        retry_backend="noop",
    )

    assert isinstance(bot._botx_api.get_http_client(), RetryingHttpClient)


def test__build_bot__retry_overrides(bot_account) -> None:
    class DummyRetryPolicy:
        async def execute(self, func):  # type: ignore[no-untyped-def]
            return await func()

    dummy_policy = DummyRetryPolicy()

    bot = build_bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        retry_enabled=True,
        retry_stream=False,
        retry_policy=dummy_policy,
    )

    client = bot._botx_api.get_http_client()
    assert isinstance(client, RetryingHttpClient)
    assert client._enabled is True
    assert client._retry_stream is False
    assert client._retry_policy is dummy_policy


def test__build_bot__dedup_overrides(bot_account) -> None:
    class DummyDedupStore:
        def __init__(self) -> None:
            self.calls: list[tuple[str, float]] = []

        async def mark_seen(self, key: str, ttl_seconds: float) -> bool:
            self.calls.append((key, ttl_seconds))
            return True

    dummy_store = DummyDedupStore()

    bot = build_bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        dedup_enabled=True,
        dedup_ttl=321.0,
        dedup_store=dummy_store,
    )

    middlewares = bot._handler_collector._middlewares
    dedup_methods = [
        mw
        for mw in middlewares
        if getattr(mw, "__func__", None) is DedupMiddleware.dispatch
    ]

    assert len(dedup_methods) == 1
    dedup_middleware = dedup_methods[0]

    class DummyBot:
        id = "bot-id"

    class DummyMessage:
        bot = DummyBot()
        sync_id = "sync-id"

    called = False

    async def call_next(message, bot):  # type: ignore[no-untyped-def]
        nonlocal called
        called = True

    asyncio.run(dedup_middleware(DummyMessage(), DummyBot(), call_next))

    assert dummy_store.calls == [("bot-id:sync-id", 321.0)]
    assert called is True


def test__build_bot__widget_state_store_override(bot_account) -> None:
    store = InMemoryWidgetStateStore()

    bot = build_bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        widget_state_store=store,
    )

    assert bot._widget_state_store is store


def test__merge_middlewares__dedup_disabled() -> None:
    dedup = object()

    class _Dummy:
        dispatch = dedup

    merged = _merge_middlewares([1, 2], False, _Dummy())

    assert merged == [1, 2]


def test__merge_middlewares__dedup_enabled() -> None:
    dedup = object()

    class _Dummy:
        dispatch = dedup

    merged = _merge_middlewares([1, 2], True, _Dummy())

    assert merged == [1, 2, dedup]


class _DummySession:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def _install_aiohttp_stub(
    monkeypatch: pytest.MonkeyPatch,
    *,
    session: _DummySession,
) -> None:
    module = types.ModuleType("aiohttp")

    class ClientError(Exception):
        pass

    class ClientTimeout:
        def __init__(self, total: float | None = None) -> None:
            self.total = total

    class FormData:
        def add_field(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            return None

    def ClientSession(*args, **kwargs):  # type: ignore[no-untyped-def]
        return session

    module.ClientError = ClientError
    module.ClientTimeout = ClientTimeout
    module.ClientSession = ClientSession
    module.FormData = FormData

    monkeypatch.setitem(sys.modules, "aiohttp", module)


@pytest.mark.asyncio
async def test__container__aiohttp_backend_selected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = _DummySession()
    _install_aiohttp_stub(monkeypatch, session=session)

    container = BotXContainer()
    container.config.from_dict(build_default_config())
    container.config.http.backend.from_value("aiohttp")

    client = container.http_client()
    assert isinstance(client, RetryingHttpClient)
    assert isinstance(client._client, AioHttpClientAdapter)

    await client.aclose()
    assert session.closed
