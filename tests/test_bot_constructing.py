import asyncio
from typing import Any, cast

import httpx
import pytest

from pybotx import (
    Bot,
    BotAccountWithSecret,
    BotXRequestMetadata,
    BotXRequestResult,
    BotXRetryPolicy,
    BotXRetryStrategy,
    BotXRetryEvent,
    HandlerCollector,
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
