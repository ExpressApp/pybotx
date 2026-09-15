import importlib

import pytest

from pybotx import (
    InMemoryIngressMetricsCollector,
    IngressCommandMetadata,
    IngressCommandResult,
    NoopIngressMetricsCollector,
    PrometheusIngressMetricsCollector,
)


def test__noop_ingress_metrics_collector__does_not_fail() -> None:
    collector = NoopIngressMetricsCollector()
    metadata = IngressCommandMetadata(
        command_kind="incoming_message",
        command_name="/demo",
    )

    collector.on_queue_depth(1)
    collector.on_command_rejected(
        metadata,
        reason="queue_overflow_reject_new",
        queue_depth=1,
    )
    collector.on_command_finished(
        metadata,
        IngressCommandResult(duration_ms=12),
        queue_depth=0,
    )


def test__in_memory_ingress_metrics_collector__collects_metrics() -> None:
    # - Arrange -
    collector = InMemoryIngressMetricsCollector()
    metadata = IngressCommandMetadata(
        command_kind="incoming_message",
        command_name="/demo",
    )
    error = RuntimeError("boom")

    # - Act -
    collector.on_queue_depth(-1)
    collector.on_command_rejected(
        metadata,
        reason="queue_overflow_reject_new",
        queue_depth=5,
    )
    collector.on_command_finished(
        metadata,
        IngressCommandResult(duration_ms=10),
        queue_depth=3,
    )
    collector.on_command_finished(
        metadata,
        IngressCommandResult(duration_ms=15, error=error),
        queue_depth=0,
    )
    snapshot = collector.snapshot()

    # - Assert -
    assert snapshot.queue_depth == 0
    assert snapshot.commands_total == 2
    assert snapshot.errors_total == 1
    assert snapshot.rejected_total == 1
    assert snapshot.latency_sum_ms == 25
    assert snapshot.command_outcomes[("incoming_message", "/demo", "ok")] == 1
    assert snapshot.command_outcomes[("incoming_message", "/demo", "error")] == 1
    assert snapshot.command_errors[("incoming_message", "/demo", "RuntimeError")] == 1
    assert snapshot.command_rejections[
        ("incoming_message", "/demo", "queue_overflow_reject_new")
    ] == 1


def test__prometheus_ingress_metrics_collector__collects_metrics() -> None:
    prometheus_client = pytest.importorskip("prometheus_client")
    registry = prometheus_client.CollectorRegistry()
    collector = PrometheusIngressMetricsCollector(registry=registry)
    metadata = IngressCommandMetadata(
        command_kind="system_event",
        command_name="CTSLoginEvent",
    )

    collector.on_queue_depth(2)
    collector.on_command_rejected(
        metadata,
        reason="queue_overflow_reject_new:reason",
        queue_depth=2,
    )
    collector.on_command_finished(
        metadata,
        IngressCommandResult(duration_ms=50),
        queue_depth=1,
    )
    collector.on_command_finished(
        metadata,
        IngressCommandResult(duration_ms=30, error=ValueError("boom")),
        queue_depth=0,
    )

    assert registry.get_sample_value("pybotx_ingress_queue_depth") == 0.0
    assert registry.get_sample_value(
        "pybotx_ingress_rejected_total",
        {
            "command_kind": "system_event",
            "command_name": "CTSLoginEvent",
            "reason": "queue_overflow_reject_new",
        },
    ) == 1.0
    assert registry.get_sample_value(
        "pybotx_ingress_commands_total",
        {
            "command_kind": "system_event",
            "command_name": "CTSLoginEvent",
            "outcome": "ok",
        },
    ) == 1.0
    assert registry.get_sample_value(
        "pybotx_ingress_commands_total",
        {
            "command_kind": "system_event",
            "command_name": "CTSLoginEvent",
            "outcome": "error",
        },
    ) == 1.0
    assert registry.get_sample_value(
        "pybotx_ingress_errors_total",
        {
            "command_kind": "system_event",
            "command_name": "CTSLoginEvent",
            "error_type": "ValueError",
        },
    ) == 1.0


def test__prometheus_ingress_metrics_collector__supports_custom_reason_normalizer() -> None:
    prometheus_client = pytest.importorskip("prometheus_client")
    registry = prometheus_client.CollectorRegistry()
    collector = PrometheusIngressMetricsCollector(
        registry=registry,
        reason_normalizer=lambda _: "custom_reason",
    )
    metadata = IngressCommandMetadata(
        command_kind="incoming_message",
        command_name="/demo",
    )

    collector.on_command_rejected(
        metadata,
        reason="queue_overflow_reject_new:details",
        queue_depth=1,
    )

    assert registry.get_sample_value(
        "pybotx_ingress_rejected_total",
        {
            "command_kind": "incoming_message",
            "command_name": "/demo",
            "reason": "custom_reason",
        },
    ) == 1.0


def test__prometheus_ingress_metrics_collector__requires_prometheus_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_import_module = importlib.import_module

    def import_module(name: str) -> object:
        if name == "prometheus_client":
            raise ModuleNotFoundError(name)
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", import_module)

    with pytest.raises(RuntimeError, match="prometheus-client"):
        PrometheusIngressMetricsCollector()
