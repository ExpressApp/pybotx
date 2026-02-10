from __future__ import annotations

from typing import Any

import httpx
from dependency_injector import containers, providers

from pybotx.application.bot import Bot
from pybotx.application.callbacks.callback_manager import CallbackManager
from pybotx.application.middlewares.dedup_middleware import DedupMiddleware
from pybotx.application.request_verifier import RequestVerifier
from pybotx.application.widgets.factory import WidgetFactory
from pybotx.domain.ports.callback_repo import CallbackRepoProto
from pybotx.domain.ports.dedup_store import DedupStorePort
from pybotx.infrastructure.bot_accounts_storage import BotAccountsStorage
from pybotx.infrastructure.callbacks.callback_memory_repo import CallbackMemoryRepo
from pybotx.domain.auth import BotXAuthVersion
from pybotx.domain.ports.http_client import HttpClientPort
from pybotx.domain.ports.jwt_encoder import JwtEncoderPort
from pybotx.domain.ports.jwt_verifier import JwtVerifierPort
from pybotx.domain.ports.logger import LoggerPort
from pybotx.domain.logger import set_logger
from pybotx.domain.ports.retry_policy import RetryPolicyPort
from pybotx.domain.ports.widget_state_store import WidgetStateStorePort
from pybotx.infrastructure.aiohttp_client import AioHttpClientAdapter
from pybotx.infrastructure.botx_api import HttpBotXApi
from pybotx.infrastructure.botx_api.method_factory import BotXApiMethodFactory
from pybotx.infrastructure.services.users_csv import UsersCsvService
from pybotx.infrastructure.dedup_store import InMemoryDedupStore, NoopDedupStore
from pybotx.infrastructure.httpx_client import HttpxClientAdapter
from pybotx.infrastructure.jwt_encoder import PyJwtEncoder
from pybotx.infrastructure.jwt_verifier import PyJwtVerifier
from pybotx.infrastructure.retry_policy import NoopRetryPolicy, TenacityRetryPolicy
from pybotx.infrastructure.retrying_http_client import RetryingHttpClient
from pybotx.infrastructure.services.attachment_factory import AttachmentFactory
from pybotx.infrastructure.widget_state_store import (
    InMemoryWidgetStateStore,
    JsonWidgetStateSerializer,
    PickleWidgetStateSerializer,
    RedisWidgetStateStore,
    WidgetStateSerializer,
)


def _merge_middlewares(
    middlewares: list[Any],
    dedup_enabled: bool,
    dedup_middleware: DedupMiddleware,
) -> list[Any]:
    merged = list(middlewares)
    if dedup_enabled:
        merged.append(dedup_middleware.dispatch)
    return merged


def _configure_logger(logger: LoggerPort | None) -> None:
    if logger is not None:
        set_logger(logger)


def _build_bot(*, logger_setup: Any, **kwargs: Any) -> Bot:
    return Bot(**kwargs)


class BotXContainer(containers.DeclarativeContainer):
    """Composition root for pybotx.

    Configure via `container.config` and build a Bot instance via `container.bot()`.

    Example:
        container = BotXContainer()
        container.config.bot.accounts.from_value([...])
        container.config.bot.collectors.from_value([...])
        bot = container.bot()
    """

    config = providers.Configuration()

    logger: providers.Provider[LoggerPort | None] = providers.Object(None)  # type: ignore[assignment]
    logger_setup = providers.Callable(_configure_logger, logger)

    jwt_encoder = providers.Singleton(PyJwtEncoder)

    bot_accounts_storage = providers.Singleton(
        BotAccountsStorage,
        bot_accounts=config.bot.accounts,
        auth_version=config.bot.auth_version.as_(BotXAuthVersion),
        jwt_encoder=jwt_encoder,
    )

    httpx_client = providers.Singleton(
        httpx.AsyncClient,
        timeout=config.http.timeout.as_float(),
    )

    httpx_adapter = providers.Singleton(
        HttpxClientAdapter,
        client=httpx_client,
    )

    aiohttp_client = providers.Singleton(
        AioHttpClientAdapter,
        timeout=config.http.timeout.as_float(),
    )

    raw_http_client: providers.Provider[HttpClientPort] = providers.Selector(  # type: ignore[assignment]
        config.http.backend,
        httpx=httpx_adapter,
        aiohttp=aiohttp_client,
    )

    retry_policy: providers.Provider[RetryPolicyPort] = providers.Selector(  # type: ignore[assignment]
        config.http.retry.backend,
        noop=providers.Singleton(NoopRetryPolicy),
        tenacity=providers.Singleton(
            TenacityRetryPolicy,
            enabled=config.http.retry.enabled.as_(bool),
            max_attempts=config.http.retry.max_attempts.as_int(),
            min_delay=config.http.retry.min_delay.as_float(),
            max_delay=config.http.retry.max_delay.as_float(),
            multiplier=config.http.retry.multiplier.as_float(),
            jitter=config.http.retry.jitter.as_(bool),
        ),
        custom=providers.Dependency(instance_of=RetryPolicyPort),
    )

    http_client = providers.Singleton(
        RetryingHttpClient,
        client=raw_http_client,
        retry_policy=retry_policy,
        enabled=config.http.retry.enabled.as_(bool),
        retry_stream=config.http.retry.retry_stream.as_(bool),
    )

    jwt_verifier = providers.Singleton(PyJwtVerifier)

    request_verifier = providers.Factory(
        RequestVerifier,
        bot_accounts_storage=bot_accounts_storage,
        jwt_verifier=jwt_verifier,
    )

    callback_repo: providers.Provider[CallbackRepoProto] = providers.Selector(  # type: ignore[assignment]
        config.callbacks.backend,
        memory=providers.Singleton(CallbackMemoryRepo),
        custom=providers.Dependency(instance_of=CallbackRepoProto),
    )

    callbacks_manager = providers.Singleton(
        CallbackManager,
        callback_repo=callback_repo,
    )

    botx_api_method_factory = providers.Factory(
        BotXApiMethodFactory,
        http_client=http_client,
        bot_accounts_storage=bot_accounts_storage,
        callbacks_manager=callbacks_manager,
    )

    users_csv_service = providers.Factory(
        UsersCsvService,
        method_factory=botx_api_method_factory,
    )

    attachment_factory = providers.Factory(AttachmentFactory)

    redis_client: providers.Provider[object] = providers.Dependency()  # type: ignore[assignment]

    widget_state_serializer: providers.Provider[WidgetStateSerializer] = providers.Selector(  # type: ignore[assignment]
        config.widgets.state_store.serializer,
        json=providers.Singleton(
            JsonWidgetStateSerializer,
            write_version=config.widgets.state_store.serializer_version.as_int(),
        ),
        pickle=providers.Singleton(PickleWidgetStateSerializer),
        custom=providers.Dependency(instance_of=WidgetStateSerializer),
    )

    widget_state_store = providers.Selector(
        config.widgets.state_store.backend,
        memory=providers.Singleton(InMemoryWidgetStateStore),
        redis=providers.Factory(
            RedisWidgetStateStore,
            redis=redis_client,
            prefix=config.widgets.state_store.redis_prefix.as_(str),
            serializer=widget_state_serializer,
        ),
        custom=providers.Dependency(instance_of=WidgetStateStorePort),
    )

    widget_factory = providers.Factory(
        WidgetFactory,
        include_state_in_metadata=config.widgets.include_state_in_metadata.as_(bool),
    )

    exception_handlers = providers.Object(None)

    dedup_store: providers.Provider[DedupStorePort] = providers.Selector(  # type: ignore[assignment]
        config.bot.dedup.backend,
        memory=providers.Singleton(InMemoryDedupStore),
        noop=providers.Singleton(NoopDedupStore),
        custom=providers.Dependency(instance_of=DedupStorePort),
    )

    dedup_middleware = providers.Factory(
        DedupMiddleware,
        store=dedup_store,
        ttl_seconds=config.bot.dedup.ttl.as_float(),
        enabled=config.bot.dedup.enabled.as_(bool),
    )

    middlewares = providers.Callable(
        _merge_middlewares,
        config.bot.middlewares,
        config.bot.dedup.enabled.as_(bool),
        dedup_middleware,
    )

    botx_api = providers.Factory(
        HttpBotXApi,
        http_client=http_client,
        bot_accounts_storage=bot_accounts_storage,
        callbacks_manager=callbacks_manager,
        method_factory=botx_api_method_factory,
        users_csv_service=users_csv_service,
        default_callback_timeout=config.bot.default_callback_timeout.as_float(),
    )

    bot = providers.Factory(
        _build_bot,
        logger_setup=logger_setup,
        collectors=config.bot.collectors,
        middlewares=middlewares,
        exception_handlers=exception_handlers,
        bot_accounts_storage=bot_accounts_storage,
        callbacks_manager=callbacks_manager,
        botx_api=botx_api,
        request_verifier=request_verifier,
        widget_state_store=widget_state_store,
    )


def build_default_config() -> dict[str, Any]:
    return {
        "http": {
            "timeout": 60.0,
            "backend": "httpx",
            "retry": {
                "enabled": False,
                "backend": "noop",
                "max_attempts": 3,
                "min_delay": 0.1,
                "max_delay": 2.0,
                "multiplier": 2.0,
                "jitter": True,
                "retry_stream": True,
            },
        },
        "callbacks": {"backend": "memory"},
        "bot": {
            "accounts": [],
            "collectors": [],
            "middlewares": [],
            "default_callback_timeout": 60.0,
            "auth_version": BotXAuthVersion.V2,
            "dedup": {
                "enabled": False,
                "ttl": 300.0,
                "backend": "memory",
            },
        },
        "widgets": {
            "include_state_in_metadata": False,
            "state_store": {
                "backend": "memory",
                "redis_prefix": "widget_state:",
                "serializer": "json",
                "serializer_version": 2,
            },
        },
    }


def build_bot(
    *,
    collectors: list[Any],
    bot_accounts: list[Any],
    middlewares: list[Any] | None = None,
    http_backend: str = "httpx",
    http_client: HttpClientPort | None = None,
    raw_http_client: HttpClientPort | None = None,
    retry_policy: RetryPolicyPort | None = None,
    retry_enabled: bool | None = None,
    retry_stream: bool | None = None,
    retry_backend: str | None = None,
    jwt_encoder: JwtEncoderPort | None = None,
    jwt_verifier: JwtVerifierPort | None = None,
    logger: LoggerPort | None = None,
    request_verifier: RequestVerifier | None = None,
    exception_handlers: Any | None = None,
    default_callback_timeout: float = 60.0,
    callback_repo: CallbackRepoProto | None = None,
    auth_version: BotXAuthVersion = BotXAuthVersion.V2,
    dedup_enabled: bool | None = None,
    dedup_ttl: float | None = None,
    dedup_store: DedupStorePort | None = None,
    widget_state_store: WidgetStateStorePort | None = None,
) -> Bot:
    """Convenience builder for Bot with default infrastructure wiring."""
    container = BotXContainer()
    container.config.from_dict(build_default_config())
    container.config.bot.accounts.from_value(bot_accounts)
    container.config.bot.collectors.from_value(collectors)
    container.config.bot.middlewares.from_value(middlewares or [])
    container.config.bot.default_callback_timeout.from_value(default_callback_timeout)
    container.config.bot.auth_version.from_value(auth_version)
    container.config.http.backend.from_value(http_backend)
    if retry_backend is not None:
        container.config.http.retry.backend.from_value(retry_backend)
    if retry_enabled is not None:
        container.config.http.retry.enabled.from_value(retry_enabled)
    if retry_stream is not None:
        container.config.http.retry.retry_stream.from_value(retry_stream)
    if dedup_enabled is not None:
        container.config.bot.dedup.enabled.from_value(dedup_enabled)
    if dedup_ttl is not None:
        container.config.bot.dedup.ttl.from_value(dedup_ttl)

    if exception_handlers is not None:
        container.exception_handlers.override(providers.Object(exception_handlers))

    if http_client is not None:
        container.http_client.override(providers.Object(http_client))
    elif raw_http_client is not None:
        container.raw_http_client.override(providers.Object(raw_http_client))

    if retry_policy is not None:
        container.retry_policy.override(providers.Object(retry_policy))

    if jwt_encoder is not None:
        container.jwt_encoder.override(providers.Object(jwt_encoder))

    if jwt_verifier is not None:
        container.jwt_verifier.override(providers.Object(jwt_verifier))

    if logger is not None:
        container.logger.override(providers.Object(logger))

    if request_verifier is not None:
        container.request_verifier.override(providers.Object(request_verifier))

    if callback_repo is not None:
        container.callback_repo.override(providers.Object(callback_repo))

    if dedup_store is not None:
        container.dedup_store.override(providers.Object(dedup_store))

    if widget_state_store is not None:
        container.widget_state_store.override(providers.Object(widget_state_store))

    return container.bot()
