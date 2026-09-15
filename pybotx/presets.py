from collections.abc import Collection, Sequence
from dataclasses import dataclass
from typing import Any

from pybotx.bot.ingress_observability import (
    BotIngressMetricsCollector,
    PrometheusIngressMetricsCollector,
    ReasonNormalizer as IngressReasonNormalizer,
)
from pybotx.client.http_config import (
    AllowedRequestPattern,
    AnyOfBotXRetryRequestPolicy,
    BotXOperation,
    BotXRetryPolicy,
    BotXRetryRequestPolicy,
    BotXRetryStrategy,
    KnownSafeBotXRetryRequestPolicy,
    OperationName,
    SafeBotXRetryRequestPolicy,
)
from pybotx.client.observability import (
    BotXRequestObserver,
    OpenTelemetryTracingCollector,
    PathNormalizer,
    PrometheusMetricsCollector,
    ReasonNormalizer as OutgoingReasonNormalizer,
    SpanEnricher,
)
from pybotx.constants import (
    BOTX_HTTP_RETRY_ATTEMPTS,
    BOTX_HTTP_RETRY_INITIAL_DELAY_SECONDS,
    BOTX_HTTP_RETRY_JITTER_SECONDS,
    BOTX_HTTP_RETRY_MAX_DELAY_SECONDS,
)


def _normalize_operation_names(
    operation_names: Collection[OperationName] | None,
) -> tuple[str, ...] | None:
    if operation_names is None:
        return None

    return tuple(
        operation_name.value
        if isinstance(operation_name, BotXOperation)
        else operation_name
        for operation_name in operation_names
    )


@dataclass(frozen=True, slots=True)
class BotRetryPreset:
    retry_policy: BotXRetryPolicy
    retry_request_policy: BotXRetryRequestPolicy
    retry_strategy: BotXRetryStrategy | None = None

    def as_bot_kwargs(self) -> dict[str, object]:
        kwargs: dict[str, object] = {
            "retry_policy": self.retry_policy,
            "retry_request_policy": self.retry_request_policy,
        }
        if self.retry_strategy is not None:
            kwargs["retry_strategy"] = self.retry_strategy
        return kwargs


@dataclass(frozen=True, slots=True)
class BotObservabilityPreset:
    metrics_collector: BotXRequestObserver | None = None
    tracing_collector: BotXRequestObserver | None = None
    ingress_metrics_collector: BotIngressMetricsCollector | None = None

    def as_bot_kwargs(self) -> dict[str, object]:
        kwargs: dict[str, object] = {}
        if self.metrics_collector is not None:
            kwargs["metrics_collector"] = self.metrics_collector
        if self.tracing_collector is not None:
            kwargs["tracing_collector"] = self.tracing_collector
        if self.ingress_metrics_collector is not None:
            kwargs["ingress_metrics_collector"] = self.ingress_metrics_collector
        return kwargs


@dataclass(frozen=True, slots=True)
class BotProductionPreset:
    retry: BotRetryPreset | None = None
    observability: BotObservabilityPreset | None = None

    def as_bot_kwargs(self) -> dict[str, object]:
        kwargs: dict[str, object] = {}
        if self.retry is not None:
            kwargs.update(self.retry.as_bot_kwargs())
        if self.observability is not None:
            kwargs.update(self.observability.as_bot_kwargs())
        return kwargs


def build_production_retry_preset(
    *,
    max_attempts: int = BOTX_HTTP_RETRY_ATTEMPTS,
    initial_delay_seconds: float = BOTX_HTTP_RETRY_INITIAL_DELAY_SECONDS,
    max_delay_seconds: float = BOTX_HTTP_RETRY_MAX_DELAY_SECONDS,
    jitter_seconds: float = BOTX_HTTP_RETRY_JITTER_SECONDS,
    retryable_status_codes: Collection[int] | None = None,
    retry_request_policy: BotXRetryRequestPolicy | None = None,
    retry_strategy: BotXRetryStrategy | None = None,
    extra_safe_requests: Collection[AllowedRequestPattern] | None = None,
    extra_safe_operations: Collection[OperationName] | None = None,
) -> BotRetryPreset:
    if retry_request_policy is not None and (
        extra_safe_requests is not None or extra_safe_operations is not None
    ):
        raise ValueError(
            "`extra_safe_requests` and `extra_safe_operations` can't be passed "
            "with custom `retry_request_policy`",
        )

    if retry_request_policy is None:
        retry_request_policy = AnyOfBotXRetryRequestPolicy(
            policies=(
                SafeBotXRetryRequestPolicy(
                    extra_safe_requests=extra_safe_requests,
                    extra_safe_operation_names=_normalize_operation_names(
                        extra_safe_operations,
                    ),
                ),
                KnownSafeBotXRetryRequestPolicy(),
            ),
        )

    if retryable_status_codes is None:
        retry_policy = BotXRetryPolicy(
            max_attempts=max_attempts,
            initial_delay_seconds=initial_delay_seconds,
            max_delay_seconds=max_delay_seconds,
            jitter_seconds=jitter_seconds,
        )
    else:
        retry_policy = BotXRetryPolicy(
            max_attempts=max_attempts,
            initial_delay_seconds=initial_delay_seconds,
            max_delay_seconds=max_delay_seconds,
            jitter_seconds=jitter_seconds,
            retryable_status_codes=frozenset(retryable_status_codes),
        )

    return BotRetryPreset(
        retry_policy=retry_policy,
        retry_request_policy=retry_request_policy,
        retry_strategy=retry_strategy,
    )


def build_production_observability_preset(
    *,
    enable_prometheus_metrics: bool = True,
    enable_open_telemetry_tracing: bool = True,
    registry: Any | None = None,
    botx_metric_prefix: str = "pybotx_botx",
    ingress_metric_prefix: str = "pybotx_ingress",
    botx_latency_buckets: Sequence[float] | None = None,
    ingress_latency_buckets: Sequence[float] | None = None,
    path_normalizer: PathNormalizer | None = None,
    retry_reason_normalizer: OutgoingReasonNormalizer | None = None,
    ingress_reason_normalizer: IngressReasonNormalizer | None = None,
    tracer_name: str = "pybotx.botx",
    tracer_provider: Any | None = None,
    span_name_template: str = "{method} {path}",
    span_enricher: SpanEnricher | None = None,
) -> BotObservabilityPreset:
    if not enable_prometheus_metrics and not enable_open_telemetry_tracing:
        raise ValueError(
            "At least one observability backend should be enabled",
        )

    metrics_collector: BotXRequestObserver | None = None
    ingress_metrics_collector: BotIngressMetricsCollector | None = None
    if enable_prometheus_metrics:
        metrics_collector = PrometheusMetricsCollector(
            registry=registry,
            metric_prefix=botx_metric_prefix,
            latency_buckets=botx_latency_buckets,
            path_normalizer=path_normalizer,
            reason_normalizer=retry_reason_normalizer,
        )
        ingress_metrics_collector = PrometheusIngressMetricsCollector(
            registry=registry,
            metric_prefix=ingress_metric_prefix,
            latency_buckets=ingress_latency_buckets,
            reason_normalizer=ingress_reason_normalizer,
        )

    tracing_collector: BotXRequestObserver | None = None
    if enable_open_telemetry_tracing:
        tracing_collector = OpenTelemetryTracingCollector(
            tracer_name=tracer_name,
            tracer_provider=tracer_provider,
            span_name_template=span_name_template,
            span_enricher=span_enricher,
        )

    return BotObservabilityPreset(
        metrics_collector=metrics_collector,
        tracing_collector=tracing_collector,
        ingress_metrics_collector=ingress_metrics_collector,
    )


def build_production_bot_preset(
    *,
    retry_preset: BotRetryPreset | None = None,
    observability_preset: BotObservabilityPreset | None = None,
) -> BotProductionPreset:
    return BotProductionPreset(
        retry=retry_preset or build_production_retry_preset(),
        observability=observability_preset or build_production_observability_preset(),
    )
