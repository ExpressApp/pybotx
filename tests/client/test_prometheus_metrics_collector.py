from uuid import UUID

import pytest

from pybotx import (
    BotXRequestMetadata,
    BotXRequestResult,
    BotXRetryEvent,
    PrometheusMetricsCollector,
)

prometheus_client = pytest.importorskip("prometheus_client")
CollectorRegistry = prometheus_client.CollectorRegistry


def test__prometheus_metrics_collector__collects_success_request_metrics() -> None:
    # - Arrange -
    registry = CollectorRegistry()
    collector = PrometheusMetricsCollector(registry=registry)
    metadata = BotXRequestMetadata(
        method="POST",
        url="https://cts.example.com/api/v4/botx/notifications/internal?x=1",
    )

    # - Act -
    collector.on_request_start(metadata)
    collector.on_request_finish(
        metadata,
        BotXRequestResult(status_code=200, duration_ms=125),
    )

    # - Assert -
    assert registry.get_sample_value(
        "pybotx_botx_requests_total",
        {
            "method": "POST",
            "path": "/api/v4/botx/notifications/internal",
            "status": "200",
            "outcome": "ok",
        },
    ) == 1.0
    assert registry.get_sample_value(
        "pybotx_botx_request_latency_seconds_count",
        {
            "method": "POST",
            "path": "/api/v4/botx/notifications/internal",
            "status": "200",
        },
    ) == 1.0
    assert registry.get_sample_value(
        "pybotx_botx_request_latency_seconds_sum",
        {
            "method": "POST",
            "path": "/api/v4/botx/notifications/internal",
            "status": "200",
        },
    ) == pytest.approx(0.125)


def test__prometheus_metrics_collector__collects_error_metrics() -> None:
    # - Arrange -
    registry = CollectorRegistry()
    collector = PrometheusMetricsCollector(registry=registry)
    metadata = BotXRequestMetadata(method="GET", url="https://cts.example.com/foo/bar")
    error = RuntimeError("boom")

    # - Act -
    collector.on_request_finish(
        metadata,
        BotXRequestResult(status_code=None, duration_ms=30, error=error),
    )

    # - Assert -
    assert registry.get_sample_value(
        "pybotx_botx_requests_total",
        {
            "method": "GET",
            "path": "/foo/bar",
            "status": "none",
            "outcome": "error",
        },
    ) == 1.0
    assert registry.get_sample_value(
        "pybotx_botx_request_errors_total",
        {
            "method": "GET",
            "path": "/foo/bar",
            "status": "none",
            "error_type": "RuntimeError",
        },
    ) == 1.0


def test__prometheus_metrics_collector__collects_retry_metrics_with_normalized_labels() -> None:
    # - Arrange -
    registry = CollectorRegistry()
    collector = PrometheusMetricsCollector(registry=registry)
    bot_id = UUID("21a9ec9e-f21f-4406-ac44-1a78d2ccf9e3")
    metadata = BotXRequestMetadata(
        method="GET",
        url=f"https://cts.example.com/api/v2/botx/bots/{bot_id}/token",
    )

    # - Act -
    collector.on_request_retry(
        metadata,
        BotXRetryEvent(
            attempt=1,
            max_attempts=3,
            sleep_seconds=0.1,
            reason="ConnectTimeout: Connection timeout",
        ),
    )

    # - Assert -
    assert registry.get_sample_value(
        "pybotx_botx_request_retries_total",
        {
            "method": "GET",
            "path": "/api/v2/botx/bots/{uuid}/token",
            "reason": "ConnectTimeout",
        },
    ) == 1.0


def test__prometheus_metrics_collector__supports_custom_normalizers() -> None:
    # - Arrange -
    registry = CollectorRegistry()

    def path_normalizer(_: str) -> str:
        return "/custom/path"

    def reason_normalizer(_: str) -> str:
        return "custom_reason"

    collector = PrometheusMetricsCollector(
        registry=registry,
        path_normalizer=path_normalizer,
        reason_normalizer=reason_normalizer,
    )
    metadata = BotXRequestMetadata(
        method="PATCH",
        url="https://cts.example.com/very/dynamic/path",
    )

    # - Act -
    collector.on_request_retry(
        metadata,
        BotXRetryEvent(
            attempt=1,
            max_attempts=2,
            sleep_seconds=0.1,
            reason="NetworkError: boom",
        ),
    )
    collector.on_request_finish(
        metadata,
        BotXRequestResult(status_code=204, duration_ms=12),
    )

    # - Assert -
    assert registry.get_sample_value(
        "pybotx_botx_request_retries_total",
        {
            "method": "PATCH",
            "path": "/custom/path",
            "reason": "custom_reason",
        },
    ) == 1.0
    assert registry.get_sample_value(
        "pybotx_botx_requests_total",
        {
            "method": "PATCH",
            "path": "/custom/path",
            "status": "204",
            "outcome": "ok",
        },
    ) == 1.0
