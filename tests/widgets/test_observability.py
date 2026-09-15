import importlib
from typing import cast

import pytest
from pybotx import Bot, IncomingMessage

from pybotx.widgets import (
    InMemoryWidgetRunnerMetricsCollector,
    NoopWidgetRunnerMetricsCollector,
    PrometheusWidgetRunnerMetricsCollector,
)
from pybotx.widgets.base import Widget
from pybotx.widgets.runner import WidgetRunnerFinishedEvent, WidgetRunnerStartedEvent


class _FakeWidget:
    command = "/confirm-demo"
    result_mode = "edit"


def _build_started_event() -> WidgetRunnerStartedEvent:
    return WidgetRunnerStartedEvent(
        message=cast(IncomingMessage, object()),
        bot=cast(Bot, object()),
        widget=cast(Widget, _FakeWidget()),
    )


def _build_finished_event(
    *,
    duration_seconds: float = 0.125,
    skipped_by_before: bool = False,
    before_results_sent: int = 0,
    after_results_sent: int = 0,
    error: Exception | None = None,
) -> WidgetRunnerFinishedEvent:
    widget = cast(Widget, _FakeWidget())
    return WidgetRunnerFinishedEvent(
        message=cast(IncomingMessage, object()),
        bot=cast(Bot, object()),
        initial_widget=widget,
        widget=widget,
        duration_seconds=duration_seconds,
        displayed=not skipped_by_before,
        skipped_by_before=skipped_by_before,
        before_results_sent=before_results_sent,
        after_results_sent=after_results_sent,
        error=error,
    )


def test__noop_widget_runner_metrics_collector__does_not_fail() -> None:
    collector = NoopWidgetRunnerMetricsCollector()

    collector.on_started(_build_started_event())
    collector.on_finished(_build_finished_event())


def test__in_memory_widget_runner_metrics_collector__collects_metrics() -> None:
    collector = InMemoryWidgetRunnerMetricsCollector()
    collector.on_started(_build_started_event())
    collector.on_finished(
        _build_finished_event(
            skipped_by_before=True,
            before_results_sent=1,
        ),
    )
    collector.on_started(_build_started_event())
    collector.on_finished(
        _build_finished_event(
            duration_seconds=0.5,
            after_results_sent=2,
            error=RuntimeError("boom"),
        ),
    )
    snapshot = collector.snapshot()

    assert snapshot.in_flight == 0
    assert snapshot.runs_total == 2
    assert snapshot.errors_total == 1
    assert snapshot.skipped_total == 1
    assert snapshot.before_results_sent_total == 1
    assert snapshot.after_results_sent_total == 2
    assert snapshot.latency_sum_seconds == pytest.approx(0.625)
    assert snapshot.run_outcomes[("_FakeWidget", "/confirm-demo", "edit", "ok")] == 1
    assert snapshot.run_outcomes[("_FakeWidget", "/confirm-demo", "edit", "error")] == 1
    assert snapshot.errors[("_FakeWidget", "/confirm-demo", "RuntimeError")] == 1
    assert snapshot.skipped[("_FakeWidget", "/confirm-demo", "edit")] == 1
    assert snapshot.result_messages[("_FakeWidget", "/confirm-demo", "before")] == 1
    assert snapshot.result_messages[("_FakeWidget", "/confirm-demo", "after")] == 2


def test__prometheus_widget_runner_metrics_collector__collects_metrics() -> None:
    prometheus_client = pytest.importorskip("prometheus_client")
    registry = prometheus_client.CollectorRegistry()
    collector = PrometheusWidgetRunnerMetricsCollector(registry=registry)

    collector.on_started(_build_started_event())
    collector.on_finished(
        _build_finished_event(
            duration_seconds=0.125,
            skipped_by_before=True,
            before_results_sent=1,
            error=ValueError("boom"),
        ),
    )

    assert registry.get_sample_value(
        "pybotx_widget_in_flight",
        {
            "widget_name": "_FakeWidget",
            "command": "/confirm-demo",
        },
    ) == 0.0
    assert registry.get_sample_value(
        "pybotx_widget_runs_total",
        {
            "widget_name": "_FakeWidget",
            "command": "/confirm-demo",
            "result_mode": "edit",
            "outcome": "error",
        },
    ) == 1.0
    assert registry.get_sample_value(
        "pybotx_widget_errors_total",
        {
            "widget_name": "_FakeWidget",
            "command": "/confirm-demo",
            "error_type": "ValueError",
        },
    ) == 1.0
    assert registry.get_sample_value(
        "pybotx_widget_skipped_total",
        {
            "widget_name": "_FakeWidget",
            "command": "/confirm-demo",
            "result_mode": "edit",
        },
    ) == 1.0
    assert registry.get_sample_value(
        "pybotx_widget_result_messages_total",
        {
            "widget_name": "_FakeWidget",
            "command": "/confirm-demo",
            "phase": "before",
        },
    ) == 1.0
    assert registry.get_sample_value(
        "pybotx_widget_latency_seconds_sum",
        {
            "widget_name": "_FakeWidget",
            "command": "/confirm-demo",
            "result_mode": "edit",
            "outcome": "error",
        },
    ) == pytest.approx(0.125)


def test__prometheus_widget_runner_metrics_collector__requires_prometheus_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_import_module = importlib.import_module

    def import_module(name: str) -> object:
        if name == "prometheus_client":
            raise ModuleNotFoundError(name)
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", import_module)

    with pytest.raises(RuntimeError, match="prometheus-client"):
        PrometheusWidgetRunnerMetricsCollector()
