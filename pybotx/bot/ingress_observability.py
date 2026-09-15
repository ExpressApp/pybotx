import importlib
from dataclasses import dataclass
from threading import Lock
from typing import Any, Protocol, TypeAlias
from collections.abc import Sequence, Callable


@dataclass(frozen=True, slots=True)
class IngressCommandMetadata:
    command_kind: str
    command_name: str


@dataclass(frozen=True, slots=True)
class IngressCommandResult:
    duration_ms: int
    error: Exception | None = None


class BotIngressMetricsCollector(Protocol):
    def on_queue_depth(self, queue_depth: int) -> None: ...  # pragma: no cover

    def on_command_rejected(  # pragma: no cover
        self,
        metadata: IngressCommandMetadata,
        *,
        reason: str,
        queue_depth: int,
    ) -> None: ...

    def on_command_finished(  # pragma: no cover
        self,
        metadata: IngressCommandMetadata,
        result: IngressCommandResult,
        *,
        queue_depth: int,
    ) -> None: ...


class NoopIngressMetricsCollector(BotIngressMetricsCollector):
    def on_queue_depth(self, queue_depth: int) -> None:
        return None

    def on_command_rejected(
        self,
        metadata: IngressCommandMetadata,
        *,
        reason: str,
        queue_depth: int,
    ) -> None:
        return None

    def on_command_finished(
        self,
        metadata: IngressCommandMetadata,
        result: IngressCommandResult,
        *,
        queue_depth: int,
    ) -> None:
        return None


OutcomeKey: TypeAlias = tuple[str, str, str]
ErrorKey: TypeAlias = tuple[str, str, str]
RejectedKey: TypeAlias = tuple[str, str, str]


@dataclass(frozen=True, slots=True)
class IngressMetricsSnapshot:
    queue_depth: int
    commands_total: int
    errors_total: int
    rejected_total: int
    latency_sum_ms: int
    command_outcomes: dict[OutcomeKey, int]
    command_errors: dict[ErrorKey, int]
    command_rejections: dict[RejectedKey, int]


class InMemoryIngressMetricsCollector(BotIngressMetricsCollector):
    def __init__(self) -> None:
        self._lock = Lock()
        self._queue_depth = 0
        self._commands_total = 0
        self._errors_total = 0
        self._rejected_total = 0
        self._latency_sum_ms = 0
        self._command_outcomes: dict[OutcomeKey, int] = {}
        self._command_errors: dict[ErrorKey, int] = {}
        self._command_rejections: dict[RejectedKey, int] = {}

    def on_queue_depth(self, queue_depth: int) -> None:
        with self._lock:
            self._queue_depth = max(queue_depth, 0)

    def on_command_rejected(
        self,
        metadata: IngressCommandMetadata,
        *,
        reason: str,
        queue_depth: int,
    ) -> None:
        with self._lock:
            self._queue_depth = max(queue_depth, 0)
            self._rejected_total += 1
            key = (
                metadata.command_kind,
                metadata.command_name,
                reason,
            )
            self._command_rejections[key] = self._command_rejections.get(key, 0) + 1

    def on_command_finished(
        self,
        metadata: IngressCommandMetadata,
        result: IngressCommandResult,
        *,
        queue_depth: int,
    ) -> None:
        with self._lock:
            self._queue_depth = max(queue_depth, 0)
            self._commands_total += 1
            duration_ms = max(result.duration_ms, 0)
            self._latency_sum_ms += duration_ms
            outcome = "ok" if result.error is None else "error"
            outcome_key = (
                metadata.command_kind,
                metadata.command_name,
                outcome,
            )
            self._command_outcomes[outcome_key] = self._command_outcomes.get(outcome_key, 0) + 1

            if result.error is not None:
                self._errors_total += 1
                error_key = (
                    metadata.command_kind,
                    metadata.command_name,
                    type(result.error).__name__,
                )
                self._command_errors[error_key] = self._command_errors.get(error_key, 0) + 1

    def snapshot(self) -> IngressMetricsSnapshot:
        with self._lock:
            return IngressMetricsSnapshot(
                queue_depth=self._queue_depth,
                commands_total=self._commands_total,
                errors_total=self._errors_total,
                rejected_total=self._rejected_total,
                latency_sum_ms=self._latency_sum_ms,
                command_outcomes=dict(self._command_outcomes),
                command_errors=dict(self._command_errors),
                command_rejections=dict(self._command_rejections),
            )


ReasonNormalizer: TypeAlias = Callable[[str], str]


class PrometheusIngressMetricsCollector(BotIngressMetricsCollector):
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
        metric_prefix: str = "pybotx_ingress",
        latency_buckets: Sequence[float] | None = None,
        reason_normalizer: ReasonNormalizer | None = None,
    ) -> None:
        try:
            prometheus_client = importlib.import_module("prometheus_client")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "PrometheusIngressMetricsCollector requires `prometheus-client`. "
                "Install with `uv add prometheus-client`.",
            ) from exc

        counter_cls = getattr(prometheus_client, "Counter")
        histogram_cls = getattr(prometheus_client, "Histogram")
        gauge_cls = getattr(prometheus_client, "Gauge")
        self._reason_normalizer = reason_normalizer or self._default_reason_normalizer
        buckets = (
            tuple(latency_buckets)
            if latency_buckets is not None
            else self.DEFAULT_LATENCY_BUCKETS
        )

        self._commands_total = counter_cls(
            f"{metric_prefix}_commands_total",
            "Total number of processed ingress commands.",
            ("command_kind", "command_name", "outcome"),
            registry=registry,
        )
        self._errors_total = counter_cls(
            f"{metric_prefix}_errors_total",
            "Total number of failed ingress command processing attempts.",
            ("command_kind", "command_name", "error_type"),
            registry=registry,
        )
        self._rejected_total = counter_cls(
            f"{metric_prefix}_rejected_total",
            "Total number of rejected ingress commands.",
            ("command_kind", "command_name", "reason"),
            registry=registry,
        )
        self._latency_seconds = histogram_cls(
            f"{metric_prefix}_latency_seconds",
            "Ingress command processing latency in seconds.",
            ("command_kind", "command_name", "outcome"),
            buckets=buckets,
            registry=registry,
        )
        self._queue_depth = gauge_cls(
            f"{metric_prefix}_queue_depth",
            "Current ingress queue depth.",
            registry=registry,
        )

    def on_queue_depth(self, queue_depth: int) -> None:
        self._queue_depth.set(max(queue_depth, 0))

    def on_command_rejected(
        self,
        metadata: IngressCommandMetadata,
        *,
        reason: str,
        queue_depth: int,
    ) -> None:
        self._rejected_total.labels(
            command_kind=metadata.command_kind,
            command_name=metadata.command_name,
            reason=self._reason_normalizer(reason),
        ).inc()
        self._queue_depth.set(max(queue_depth, 0))

    def on_command_finished(
        self,
        metadata: IngressCommandMetadata,
        result: IngressCommandResult,
        *,
        queue_depth: int,
    ) -> None:
        outcome = "ok" if result.error is None else "error"
        self._commands_total.labels(
            command_kind=metadata.command_kind,
            command_name=metadata.command_name,
            outcome=outcome,
        ).inc()
        self._latency_seconds.labels(
            command_kind=metadata.command_kind,
            command_name=metadata.command_name,
            outcome=outcome,
        ).observe(max(result.duration_ms, 0) / 1000.0)
        if result.error is not None:
            self._errors_total.labels(
                command_kind=metadata.command_kind,
                command_name=metadata.command_name,
                error_type=type(result.error).__name__,
            ).inc()
        self._queue_depth.set(max(queue_depth, 0))

    @staticmethod
    def _default_reason_normalizer(reason: str) -> str:
        return reason.split(":", maxsplit=1)[0]
