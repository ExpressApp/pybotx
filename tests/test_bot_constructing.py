import asyncio
from typing import Any, cast
from uuid import UUID

import httpx
import pytest

from pybotx import (
    Bot,
    BotAccountWithSecret,
    BotXOperation,
    BotCommandProcessingConfig,
    BotXRequestMetadata,
    BotXRequestResult,
    BotXRetryPolicy,
    BotXRetryStrategy,
    BotXRetryEvent,
    HandlerCollector,
    InMemoryIngressMetricsCollector,
    IngressCommandMetadata,
    IngressCommandResult,
    KnownSafeBotXRetryRequestPolicy,
    OperationNameAllowlistBotXRetryRequestPolicy,
    RetryAllBotXRequestsPolicy,
    SafeBotXRetryRequestPolicy,
    build_default_httpx_limits,
    build_default_httpx_timeout,
)


def test__bot__empty_collectors_warning(
    loguru_caplog: pytest.LogCaptureFixture,
    bot_account: BotAccountWithSecret,
) -> None:
    # - Act -
    Bot(collectors=[], bot_accounts=[bot_account])

    # - Assert -
    assert "Bot has no connected collectors" in loguru_caplog.text


def test__bot__empty_bot_accounts_warning(
    loguru_caplog: pytest.LogCaptureFixture,
) -> None:
    # - Act -
    Bot(collectors=[HandlerCollector()], bot_accounts=[])

    # - Assert -
    assert "Bot has no bot accounts" in loguru_caplog.text


def test__bot__default_httpx_client_created_with_explicit_limits_and_timeout(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    expected_timeout = build_default_httpx_timeout()
    expected_limits = build_default_httpx_limits()

    # - Act -
    bot = Bot(collectors=[HandlerCollector()], bot_accounts=[bot_account])

    # - Assert -
    assert bot._httpx_client.timeout == expected_timeout
    transport = cast(Any, bot._httpx_client._transport)
    assert transport._pool._max_connections == (
        expected_limits.max_connections
    )
    assert transport._pool._max_keepalive_connections == (
        expected_limits.max_keepalive_connections
    )


def test__bot__custom_httpx_client_with_http_settings_raises_value_error(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    custom_httpx_client = httpx.AsyncClient()

    try:
        # - Act / Assert -
        with pytest.raises(ValueError):
            Bot(
                collectors=[HandlerCollector()],
                bot_accounts=[bot_account],
                httpx_client=custom_httpx_client,
                httpx_timeout=httpx.Timeout(timeout=1.0),
            )
    finally:
        asyncio.run(custom_httpx_client.aclose())


def test__bot__passes_retry_policy_to_accounts_storage(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    retry_policy = BotXRetryPolicy(max_attempts=2)

    # - Act -
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        retry_policy=retry_policy,
    )

    # - Assert -
    assert bot._bot_accounts_storage.get_retry_policy() == retry_policy


def test__bot__passes_retry_strategy_to_accounts_storage(
    bot_account: BotAccountWithSecret,
) -> None:
    class _RetryStrategy(BotXRetryStrategy):
        def build_retrying(self, **_kwargs: Any) -> Any:
            raise NotImplementedError

    retry_strategy = _RetryStrategy()

    # - Act -
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        retry_policy=BotXRetryPolicy(max_attempts=2),
        retry_strategy=retry_strategy,
    )

    # - Assert -
    assert bot._bot_accounts_storage.get_retry_strategy() is retry_strategy


def test__bot__uses_safe_retry_request_policy_by_default_when_retry_enabled(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Act -
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        retry_policy=BotXRetryPolicy(max_attempts=2),
    )

    # - Assert -
    assert isinstance(
        bot._bot_accounts_storage.get_retry_request_policy(),
        SafeBotXRetryRequestPolicy,
    )


def test__bot__passes_retry_request_policy_to_accounts_storage(
    bot_account: BotAccountWithSecret,
) -> None:
    retry_request_policy = RetryAllBotXRequestsPolicy()

    # - Act -
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        retry_policy=BotXRetryPolicy(max_attempts=2),
        retry_request_policy=retry_request_policy,
    )

    # - Assert -
    assert bot._bot_accounts_storage.get_retry_request_policy() is retry_request_policy


def test__bot__known_safe_retry_request_policy_is_supported(
    bot_account: BotAccountWithSecret,
) -> None:
    retry_request_policy = KnownSafeBotXRetryRequestPolicy()

    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        retry_policy=BotXRetryPolicy(max_attempts=2),
        retry_request_policy=retry_request_policy,
    )

    assert bot._bot_accounts_storage.get_retry_request_policy() is retry_request_policy


def test__bot__retry_disabled_by_default(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Act -
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )

    # - Assert -
    assert bot._bot_accounts_storage.get_retry_policy() is None
    assert bot._bot_accounts_storage.get_retry_request_policy() is None


def test__bot__retry_all_policy_logs_warning(
    loguru_caplog: pytest.LogCaptureFixture,
    bot_account: BotAccountWithSecret,
) -> None:
    Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        retry_policy=BotXRetryPolicy(max_attempts=2),
        retry_request_policy=RetryAllBotXRequestsPolicy(),
    )

    assert "RetryAllBotXRequestsPolicy retries all BotX requests" in loguru_caplog.text


def test__bot__operation_allowlist_with_unsafe_operation_logs_warning(
    loguru_caplog: pytest.LogCaptureFixture,
    bot_account: BotAccountWithSecret,
) -> None:
    Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        retry_policy=BotXRetryPolicy(max_attempts=2),
        retry_request_policy=OperationNameAllowlistBotXRetryRequestPolicy(
            operation_names={BotXOperation.DIRECT_NOTIFICATION},
        ),
    )

    assert "OperationNameAllowlistBotXRetryRequestPolicy allows operations" in (
        loguru_caplog.text
    )


def test__bot__known_safe_retry_policy_does_not_log_warning(
    loguru_caplog: pytest.LogCaptureFixture,
    bot_account: BotAccountWithSecret,
) -> None:
    Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        retry_policy=BotXRetryPolicy(max_attempts=2),
        retry_request_policy=KnownSafeBotXRetryRequestPolicy(),
    )

    assert "known-safe catalog" not in loguru_caplog.text


def test__bot__observability_disabled_by_default(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Act -
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )

    # - Assert -
    assert list(bot._bot_accounts_storage.iter_request_observers()) == []


def test__bot__ingress_observability_enabled_by_default(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Act -
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )

    # - Assert -
    assert isinstance(bot._ingress_metrics_collector, InMemoryIngressMetricsCollector)
    assert bot._handler_collector._ingress_metrics_collector is bot._ingress_metrics_collector


def test__bot__passes_custom_ingress_metrics_collector(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    class _IngressCollector:
        def on_queue_depth(self, queue_depth: int) -> None:
            pass

        def on_command_rejected(
            self,
            metadata: IngressCommandMetadata,
            *,
            reason: str,
            queue_depth: int,
        ) -> None:
            pass

        def on_command_finished(
            self,
            metadata: IngressCommandMetadata,
            result: IngressCommandResult,
            *,
            queue_depth: int,
        ) -> None:
            pass

    ingress_metrics_collector = _IngressCollector()

    # - Act -
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        ingress_metrics_collector=ingress_metrics_collector,
    )

    # - Assert -
    assert bot._ingress_metrics_collector is ingress_metrics_collector
    assert bot._handler_collector._ingress_metrics_collector is ingress_metrics_collector


def test__bot__passes_metrics_and_tracing_collectors(
    bot_account: BotAccountWithSecret,
) -> None:
    class _Observer:
        def on_request_start(self, metadata: BotXRequestMetadata) -> None:
            pass

        def on_request_retry(
            self,
            metadata: BotXRequestMetadata,
            retry_event: BotXRetryEvent,
        ) -> None:
            pass

        def on_request_finish(
            self,
            metadata: BotXRequestMetadata,
            result: BotXRequestResult,
        ) -> None:
            pass

    metrics_collector = _Observer()
    tracing_collector = _Observer()

    # - Act -
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        metrics_collector=metrics_collector,
        tracing_collector=tracing_collector,
    )

    # - Assert -
    assert list(bot._bot_accounts_storage.iter_request_observers()) == [
        metrics_collector,
        tracing_collector,
    ]


def test__bot__passes_command_processing_config_to_handler_collector(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    command_processing_config = BotCommandProcessingConfig(
        max_concurrency=3,
        max_queue_size=50,
    )

    # - Act -
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        command_processing_config=command_processing_config,
    )

    # - Assert -
    assert (
        bot._handler_collector._command_processing_config
        == command_processing_config
    )


def test__bot__passes_expired_sync_ids_config_to_callback_manager(
    bot_account: BotAccountWithSecret,
) -> None:
    # - Arrange -
    expired_sync_ids_ttl_seconds = 120.0
    expired_sync_ids_limit = 20_000

    # - Act -
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
        expired_sync_ids_ttl_seconds=expired_sync_ids_ttl_seconds,
        expired_sync_ids_limit=expired_sync_ids_limit,
    )

    # - Assert -
    assert (
        bot._callbacks_manager._expired_sync_ids_ttl_seconds
        == expired_sync_ids_ttl_seconds
    )
    assert bot._callbacks_manager._expired_sync_ids_limit == expired_sync_ids_limit


def test__bot__invalid_expired_sync_ids_ttl_raises_value_error(
    bot_account: BotAccountWithSecret,
) -> None:
    with pytest.raises(ValueError, match="Expired sync ids ttl should be greater than 0"):
        Bot(
            collectors=[HandlerCollector()],
            bot_accounts=[bot_account],
            expired_sync_ids_ttl_seconds=0,
        )


def test__bot__invalid_expired_sync_ids_limit_raises_value_error(
    bot_account: BotAccountWithSecret,
) -> None:
    with pytest.raises(
        ValueError,
        match="Expired sync ids limit should be greater than 0",
    ):
        Bot(
            collectors=[HandlerCollector()],
            bot_accounts=[bot_account],
            expired_sync_ids_limit=0,
        )


def test__bot__extract_request_id_prefers_headers(
    bot_account: BotAccountWithSecret,
) -> None:
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )

    assert bot._extract_request_id(
        {"sync_id": "sync-id"},
        {"X-Request-Id": "header-request-id"},
    ) == "header-request-id"
    assert bot._extract_request_id(
        {"sync_id": "sync-id"},
        None,
    ) == "sync-id"
    assert bot._extract_request_id(None, None) is None


def test__bot__extract_trace_id_from_headers_and_fallback(
    bot_account: BotAccountWithSecret,
) -> None:
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )

    assert bot._extract_trace_id({"X-Trace-Id": "trace-id"}, "fallback") == "trace-id"
    assert (
        bot._extract_trace_id(
            {"traceparent": "00-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-bbbbbbbbbbbbbbbb-01"},
            "fallback",
        )
        == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    )
    assert bot._extract_trace_id({"b3": "aaaaaaaaaaaaaaaa-1-0"}, "fallback") == (
        "aaaaaaaaaaaaaaaa"
    )
    assert bot._extract_trace_id({"traceparent": "invalid", "b3": "invalid"}, "fallback") == (
        "fallback"
    )


def test__bot__extract_bot_and_chat_id_from_payload(
    bot_account: BotAccountWithSecret,
) -> None:
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )

    assert bot._extract_bot_id({"bot_id": "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3"}) == UUID(
        "21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3",
    )
    assert bot._extract_bot_id({"bot_id": 1}) is None
    assert bot._extract_chat_id(
        {"from": {"group_chat_id": "d4d3d774-1f90-4b53-9b92-7f3867dbb2f8"}},
    ) == UUID("d4d3d774-1f90-4b53-9b92-7f3867dbb2f8")
    assert bot._extract_chat_id(
        {"group_chat_id": "2fa2f2a8-22de-4ba7-8da1-7faeb2975bb0"},
    ) == UUID("2fa2f2a8-22de-4ba7-8da1-7faeb2975bb0")
    assert bot._extract_chat_id({"from": "not-a-mapping"}) is None


def test__bot__normalize_correlation_value(
    bot_account: BotAccountWithSecret,
) -> None:
    bot = Bot(
        collectors=[HandlerCollector()],
        bot_accounts=[bot_account],
    )

    assert bot._normalize_correlation_value("  value  ") == "value"
    assert bot._normalize_correlation_value("") is None
    assert bot._normalize_correlation_value(None) is None
    assert bot._normalize_correlation_value("a" * 256) == "a" * 128
