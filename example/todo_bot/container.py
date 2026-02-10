from __future__ import annotations

from dependency_injector import containers, providers

from pybotx import BotXAuthVersion, WidgetFactory, WidgetSession, build_bot
from pybotx.domain.ports.http_client import HttpClientPort
from pybotx.infrastructure.dedup_store import InMemoryDedupStore, NoopDedupStore
from pybotx.infrastructure.retry_policy import NoopRetryPolicy, TenacityRetryPolicy
from pybotx.infrastructure.widget_state_store import (
    InMemoryWidgetStateStore,
    JsonWidgetStateSerializer,
    PickleWidgetStateSerializer,
    RedisWidgetStateStore,
    WidgetStateSerializer,
)
from pybotx.domain.ports.widget_state_store import WidgetStateStorePort

from example.todo_bot.application.services import TodoService
from example.todo_bot.infrastructure.clock import SystemClock
from example.todo_bot.infrastructure.memory_repo import InMemoryTodoRepository
from example.todo_bot.presentation.aiohttp_app import create_aiohttp_app
from example.todo_bot.presentation.fastapi_app import create_app
from pybotx.infrastructure.services.attachment_factory import AttachmentFactory

from example.todo_bot.presentation.handlers import build_collector


class TodoBotContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    clock = providers.Singleton(SystemClock)

    todo_repository = providers.Selector(
        config.storage.backend,
        memory=providers.Singleton(InMemoryTodoRepository),
    )

    todo_service = providers.Factory(
        TodoService,
        repo=todo_repository,
        clock=clock,
    )

    attachment_factory = providers.Singleton(AttachmentFactory)

    widget_factory = providers.Factory(
        WidgetFactory,
        include_state_in_metadata=config.widgets.include_state_in_metadata.as_(bool),
    )

    raw_http_client: providers.Provider[HttpClientPort | None] = providers.Object(  # type: ignore[assignment]
        None
    )

    redis_client: providers.Provider[object] = providers.Dependency()  # type: ignore[assignment]

    retry_policy = providers.Selector(
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
    )

    dedup_store = providers.Selector(
        config.bot.dedup.backend,
        memory=providers.Singleton(InMemoryDedupStore),
        noop=providers.Singleton(NoopDedupStore),
    )

    widget_state_serializer: providers.Provider[WidgetStateSerializer] = providers.Selector(  # type: ignore[assignment]
        config.widgets.state_store.serializer,
        json=providers.Singleton(
            JsonWidgetStateSerializer,
            write_version=config.widgets.state_store.serializer_version.as_int(),
        ),
        pickle=providers.Singleton(PickleWidgetStateSerializer),
        custom=providers.Dependency(instance_of=WidgetStateSerializer),
    )

    widget_state_store: providers.Provider[WidgetStateStorePort] = providers.Selector(  # type: ignore[assignment]
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

    widget_session_factory = providers.DelegatedFactory(
        WidgetSession,
        store=widget_state_store,
    )

    handler_collector = providers.Factory(
        build_collector,
        todo_service=todo_service,
        attachment_factory=attachment_factory,
        widget_factory=widget_factory,
        widget_session_factory=widget_session_factory,
        demo_enabled=config.demo.enabled.as_(bool),
        demo_allow_risky=config.demo.allow_risky.as_(bool),
    )

    collectors = providers.Callable(lambda collector: [collector], handler_collector)

    bot = providers.Factory(
        build_bot,
        collectors=collectors,
        bot_accounts=config.bot.accounts,
        auth_version=config.bot.auth_version.as_(BotXAuthVersion),
        http_backend=config.http.backend,
        raw_http_client=raw_http_client,
        retry_policy=retry_policy,
        retry_enabled=config.http.retry.enabled.as_(bool),
        retry_stream=config.http.retry.retry_stream.as_(bool),
        dedup_enabled=config.bot.dedup.enabled.as_(bool),
        dedup_ttl=config.bot.dedup.ttl.as_float(),
        dedup_store=dedup_store,
        widget_state_store=widget_state_store,
    )

    fastapi_app = providers.Factory(
        create_app,
        bot=bot,
        verify_requests=config.bot.verify_requests.as_(bool),
    )

    aiohttp_app = providers.Factory(
        create_aiohttp_app,
        bot=bot,
        verify_requests=config.bot.verify_requests.as_(bool),
    )
