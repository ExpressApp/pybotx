import importlib
from collections.abc import Sequence
from dataclasses import dataclass
from threading import Lock
from typing import Any, TypeAlias

from pybotx.widgets.runner import (
    WidgetRunnerFinishedEvent,
    WidgetRunnerObserver,
    WidgetRunnerStartedEvent,
)

RunOutcomeKey: TypeAlias = tuple[str, str, str, str]
ErrorKey: TypeAlias = tuple[str, str, str]
SkippedKey: TypeAlias = tuple[str, str, str]
ResultMessagesKey: TypeAlias = tuple[str, str, str]


class NoopWidgetRunnerMetricsCollector(WidgetRunnerObserver):
    def on_started(self, event: WidgetRunnerStartedEvent) -> None:
        return None

    def on_finished(self, event: WidgetRunnerFinishedEvent) -> None:
        return None


@dataclass(frozen=True, slots=True)
class WidgetRunnerMetricsSnapshot:
    in_flight: int
    runs_total: int
    errors_total: int
    skipped_total: int
    before_results_sent_total: int
    after_results_sent_total: int
    latency_sum_seconds: float
    run_outcomes: dict[RunOutcomeKey, int]
    errors: dict[ErrorKey, int]
    skipped: dict[SkippedKey, int]
    result_messages: dict[ResultMessagesKey, int]


class InMemoryWidgetRunnerMetricsCollector(WidgetRunnerObserver):
    def __init__(self) -> None:
        self._lock = Lock()
        self._in_flight = 0
        self._runs_total = 0
        self._errors_total = 0
        self._skipped_total = 0
        self._before_results_sent_total = 0
        self._after_results_sent_total = 0
        self._latency_sum_seconds = 0.0
        self._run_outcomes: dict[RunOutcomeKey, int] = {}
        self._errors: dict[ErrorKey, int] = {}
        self._skipped: dict[SkippedKey, int] = {}
        self._result_messages: dict[ResultMessagesKey, int] = {}

    def on_started(self, event: WidgetRunnerStartedEvent) -> None:
        with self._lock:
            self._in_flight += 1

    def on_finished(self, event: WidgetRunnerFinishedEvent) -> None:
        with self._lock:
            self._in_flight = max(self._in_flight - 1, 0)
            self._runs_total += 1
            self._latency_sum_seconds += max(event.duration_seconds, 0.0)
            self._before_results_sent_total += max(event.before_results_sent, 0)
            self._after_results_sent_total += max(event.after_results_sent, 0)

            outcome = "ok" if event.error is None else "error"
            outcome_key = (
                event.widget_name,
                event.command,
                event.result_mode,
                outcome,
            )
            self._run_outcomes[outcome_key] = self._run_outcomes.get(outcome_key, 0) + 1

            if event.before_results_sent > 0:
                before_key = (
                    event.widget_name,
                    event.command,
                    "before",
                )
                self._result_messages[before_key] = (
                    self._result_messages.get(before_key, 0) + event.before_results_sent
                )

            if event.after_results_sent > 0:
                after_key = (
                    event.widget_name,
                    event.command,
                    "after",
                )
                self._result_messages[after_key] = (
                    self._result_messages.get(after_key, 0) + event.after_results_sent
                )

            if event.skipped_by_before:
                self._skipped_total += 1
                skipped_key = (
                    event.widget_name,
                    event.command,
                    event.result_mode,
                )
                self._skipped[skipped_key] = self._skipped.get(skipped_key, 0) + 1

            if event.error is not None:
                self._errors_total += 1
                error_key = (
                    event.widget_name,
                    event.command,
                    type(event.error).__name__,
                )
                self._errors[error_key] = self._errors.get(error_key, 0) + 1

    def snapshot(self) -> WidgetRunnerMetricsSnapshot:
        with self._lock:
            return WidgetRunnerMetricsSnapshot(
                in_flight=self._in_flight,
                runs_total=self._runs_total,
                errors_total=self._errors_total,
                skipped_total=self._skipped_total,
                before_results_sent_total=self._before_results_sent_total,
                after_results_sent_total=self._after_results_sent_total,
                latency_sum_seconds=self._latency_sum_seconds,
                run_outcomes=dict(self._run_outcomes),
                errors=dict(self._errors),
                skipped=dict(self._skipped),
                result_messages=dict(self._result_messages),
            )


class PrometheusWidgetRunnerMetricsCollector(WidgetRunnerObserver):
    DEFAULT_LATENCY_BUCKETS = (
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
    )

    def __init__(
        self,
        *,
        registry: Any | None = None,
        metric_prefix: str = "pybotx_widget",
        latency_buckets: Sequence[float] | None = None,
    ) -> None:
        try:
            prometheus_client = importlib.import_module("prometheus_client")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "PrometheusWidgetRunnerMetricsCollector requires `prometheus-client`. "
                "Install with `uv add prometheus-client`.",
            ) from exc

        counter_cls = getattr(prometheus_client, "Counter")
        gauge_cls = getattr(prometheus_client, "Gauge")
        histogram_cls = getattr(prometheus_client, "Histogram")
        buckets = (
            tuple(latency_buckets)
            if latency_buckets is not None
            else self.DEFAULT_LATENCY_BUCKETS
        )

        self._runs_total = counter_cls(
            f"{metric_prefix}_runs_total",
            "Total number of widget runner executions.",
            ("widget_name", "command", "result_mode", "outcome"),
            registry=registry,
        )
        self._errors_total = counter_cls(
            f"{metric_prefix}_errors_total",
            "Total number of failed widget runner executions.",
            ("widget_name", "command", "error_type"),
            registry=registry,
        )
        self._skipped_total = counter_cls(
            f"{metric_prefix}_skipped_total",
            "Total number of widget runs skipped by before-hooks.",
            ("widget_name", "command", "result_mode"),
            registry=registry,
        )
        self._result_messages_total = counter_cls(
            f"{metric_prefix}_result_messages_total",
            "Total number of result messages sent by widget runner hooks.",
            ("widget_name", "command", "phase"),
            registry=registry,
        )
        self._latency_seconds = histogram_cls(
            f"{metric_prefix}_latency_seconds",
            "Widget runner latency in seconds.",
            ("widget_name", "command", "result_mode", "outcome"),
            buckets=buckets,
            registry=registry,
        )
        self._in_flight = gauge_cls(
            f"{metric_prefix}_in_flight",
            "Current number of widget runs in flight.",
            ("widget_name", "command"),
            registry=registry,
        )

    def on_started(self, event: WidgetRunnerStartedEvent) -> None:
        self._in_flight.labels(
            widget_name=event.widget_name,
            command=event.command,
        ).inc()

    def on_finished(self, event: WidgetRunnerFinishedEvent) -> None:
        self._in_flight.labels(
            widget_name=event.widget_name,
            command=event.command,
        ).dec()

        outcome = "ok" if event.error is None else "error"
        self._runs_total.labels(
            widget_name=event.widget_name,
            command=event.command,
            result_mode=event.result_mode,
            outcome=outcome,
        ).inc()
        self._latency_seconds.labels(
            widget_name=event.widget_name,
            command=event.command,
            result_mode=event.result_mode,
            outcome=outcome,
        ).observe(max(event.duration_seconds, 0.0))

        if event.before_results_sent > 0:
            self._result_messages_total.labels(
                widget_name=event.widget_name,
                command=event.command,
                phase="before",
            ).inc(event.before_results_sent)

        if event.after_results_sent > 0:
            self._result_messages_total.labels(
                widget_name=event.widget_name,
                command=event.command,
                phase="after",
            ).inc(event.after_results_sent)

        if event.skipped_by_before:
            self._skipped_total.labels(
                widget_name=event.widget_name,
                command=event.command,
                result_mode=event.result_mode,
            ).inc()

        if event.error is not None:
            self._errors_total.labels(
                widget_name=event.widget_name,
                command=event.command,
                error_type=type(event.error).__name__,
            ).inc()
