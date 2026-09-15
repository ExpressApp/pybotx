from dataclasses import dataclass
import importlib
import re
from contextvars import ContextVar
from collections.abc import Callable, Sequence
from typing import Any, Protocol, TypeAlias
from urllib.parse import urlsplit


@dataclass(frozen=True, slots=True)
class BotXRequestMetadata:
    method: str
    url: str
    operation_name: str | None = None
    is_streaming: bool = False


@dataclass(frozen=True, slots=True)
class BotXRetryEvent:
    attempt: int
    max_attempts: int
    sleep_seconds: float
    reason: str


@dataclass(frozen=True, slots=True)
class BotXRequestResult:
    status_code: int | None
    duration_ms: int
    error: Exception | None = None


class BotXRequestObserver(Protocol):
    def on_request_start(  # pragma: no cover
        self,
        metadata: BotXRequestMetadata,
    ) -> None: ...

    def on_request_retry(  # pragma: no cover
        self,
        metadata: BotXRequestMetadata,
        retry_event: BotXRetryEvent,
    ) -> None: ...

    def on_request_finish(  # pragma: no cover
        self,
        metadata: BotXRequestMetadata,
        result: BotXRequestResult,
    ) -> None: ...


PathNormalizer: TypeAlias = Callable[[str], str]
ReasonNormalizer: TypeAlias = Callable[[str], str]
SpanEnricher: TypeAlias = Callable[[Any, BotXRequestMetadata], None]


_UUID_PATH_SEGMENT_RE = re.compile(
    r"/[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}(?=/|$)",
)


class PrometheusMetricsCollector(BotXRequestObserver):
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
        metric_prefix: str = "pybotx_botx",
        latency_buckets: Sequence[float] | None = None,
        path_normalizer: PathNormalizer | None = None,
        reason_normalizer: ReasonNormalizer | None = None,
    ) -> None:
        try:
            prometheus_client = importlib.import_module("prometheus_client")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "PrometheusMetricsCollector requires `prometheus-client`. "
                "Install with `uv add prometheus-client`.",
            ) from exc

        counter_cls = getattr(prometheus_client, "Counter")
        histogram_cls = getattr(prometheus_client, "Histogram")
        buckets = (
            tuple(latency_buckets)
            if latency_buckets is not None
            else self.DEFAULT_LATENCY_BUCKETS
        )
        self._path_normalizer = path_normalizer or self._default_path_normalizer
        self._reason_normalizer = (
            reason_normalizer or self._default_reason_normalizer
        )

        self._requests_total = counter_cls(
            f"{metric_prefix}_requests_total",
            "Total number of outgoing BotX requests.",
            ("method", "path", "status", "outcome"),
            registry=registry,
        )
        self._request_errors_total = counter_cls(
            f"{metric_prefix}_request_errors_total",
            "Total number of failed outgoing BotX requests.",
            ("method", "path", "status", "error_type"),
            registry=registry,
        )
        self._request_retries_total = counter_cls(
            f"{metric_prefix}_request_retries_total",
            "Total number of BotX request retries.",
            ("method", "path", "reason"),
            registry=registry,
        )
        self._request_latency_seconds = histogram_cls(
            f"{metric_prefix}_request_latency_seconds",
            "Latency of outgoing BotX requests in seconds.",
            ("method", "path", "status"),
            buckets=buckets,
            registry=registry,
        )

    def on_request_start(self, metadata: BotXRequestMetadata) -> None:
        # No in-flight metric by default. Start hook is preserved for future extensions.
        return None

    def on_request_retry(
        self,
        metadata: BotXRequestMetadata,
        retry_event: BotXRetryEvent,
    ) -> None:
        self._request_retries_total.labels(
            method=metadata.method,
            path=self._path_label(metadata.url),
            reason=self._reason_label(retry_event.reason),
        ).inc()

    def on_request_finish(
        self,
        metadata: BotXRequestMetadata,
        result: BotXRequestResult,
    ) -> None:
        path = self._path_label(metadata.url)
        status = self._status_label(result.status_code)
        outcome = "ok" if result.error is None else "error"

        self._requests_total.labels(
            method=metadata.method,
            path=path,
            status=status,
            outcome=outcome,
        ).inc()
        self._request_latency_seconds.labels(
            method=metadata.method,
            path=path,
            status=status,
        ).observe(max(result.duration_ms, 0) / 1000.0)

        if result.error is not None:
            self._request_errors_total.labels(
                method=metadata.method,
                path=path,
                status=status,
                error_type=type(result.error).__name__,
            ).inc()

    def _path_label(self, url: str) -> str:
        return self._path_normalizer(url)

    def _status_label(self, status_code: int | None) -> str:
        if status_code is None:
            return "none"
        return str(status_code)

    def _reason_label(self, reason: str) -> str:
        return self._reason_normalizer(reason)

    @staticmethod
    def _default_path_normalizer(url: str) -> str:
        parsed = urlsplit(url)
        path = parsed.path or "/"
        return _UUID_PATH_SEGMENT_RE.sub("/{uuid}", path)

    @staticmethod
    def _default_reason_normalizer(reason: str) -> str:
        if reason.startswith("status_code="):
            return reason
        # Keep retry reason low-cardinality for metrics (exception class expected).
        return reason.split(":", maxsplit=1)[0]


class OpenTelemetryTracingCollector(BotXRequestObserver):
    _span_stack_var: ContextVar[tuple[Any, ...]] = ContextVar(
        "pybotx_open_telemetry_spans",
        default=(),
    )

    def __init__(
        self,
        *,
        tracer_name: str = "pybotx.botx",
        span_name_template: str = "{method} {path}",
        tracer_provider: Any | None = None,
        span_enricher: SpanEnricher | None = None,
    ) -> None:
        try:
            trace_api = importlib.import_module("opentelemetry.trace")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "OpenTelemetryTracingCollector requires `opentelemetry-api`. "
                "Install with `uv add opentelemetry-api`.",
            ) from exc

        self._trace_api = trace_api
        self._tracer_name = tracer_name
        self._span_name_template = span_name_template
        self._span_enricher = span_enricher
        if tracer_provider is None:
            self._tracer = trace_api.get_tracer(tracer_name)
        else:
            self._tracer = trace_api.get_tracer(
                tracer_name,
                tracer_provider=tracer_provider,
            )

    def on_request_start(self, metadata: BotXRequestMetadata) -> None:
        parsed = urlsplit(metadata.url)
        path = parsed.path or "/"
        span_name = self._span_name_template.format(method=metadata.method, path=path)

        span_kind = getattr(self._trace_api, "SpanKind", None)
        if span_kind is None:
            span = self._tracer.start_span(span_name)
        else:
            span = self._tracer.start_span(span_name, kind=span_kind.CLIENT)

        span.set_attribute("http.method", metadata.method)
        span.set_attribute("http.url", metadata.url)
        span.set_attribute("http.target", path)
        if parsed.hostname is not None:
            span.set_attribute("server.address", parsed.hostname)
        if parsed.port is not None:
            span.set_attribute("server.port", parsed.port)

        if self._span_enricher is not None:
            try:
                self._span_enricher(span, metadata)
            except Exception as exc:
                span.record_exception(exc)
                status_cls = getattr(self._trace_api, "Status", None)
                status_code_cls = getattr(self._trace_api, "StatusCode", None)
                if status_cls is not None and status_code_cls is not None:
                    span.set_status(status_cls(status_code_cls.ERROR, str(exc)))
                span.end()
                raise

        self._push_span(span)

    def on_request_retry(
        self,
        metadata: BotXRequestMetadata,
        retry_event: BotXRetryEvent,
    ) -> None:
        span = self._peek_span()
        if span is None:
            return

        span.add_event(
            "botx.retry",
            attributes={
                "retry.attempt": retry_event.attempt,
                "retry.max_attempts": retry_event.max_attempts,
                "retry.sleep_seconds": retry_event.sleep_seconds,
                "retry.reason": retry_event.reason,
                "http.method": metadata.method,
            },
        )

    def on_request_finish(
        self,
        metadata: BotXRequestMetadata,
        result: BotXRequestResult,
    ) -> None:
        span = self._pop_span()
        if span is None:
            return

        span.set_attribute("botx.duration_ms", result.duration_ms)
        if result.status_code is not None:
            span.set_attribute("http.status_code", result.status_code)

        status_cls = getattr(self._trace_api, "Status", None)
        status_code_cls = getattr(self._trace_api, "StatusCode", None)

        if result.error is not None:
            span.record_exception(result.error)
            if status_cls is not None and status_code_cls is not None:
                span.set_status(
                    status_cls(status_code_cls.ERROR, str(result.error)),
                )
        elif status_cls is not None and status_code_cls is not None:
            span.set_status(status_cls(status_code_cls.OK))

        span.end()

    def _push_span(self, span: Any) -> None:
        span_stack = self._span_stack_var.get()
        self._span_stack_var.set((*span_stack, span))

    def _peek_span(self) -> Any | None:
        span_stack = self._span_stack_var.get()
        if not span_stack:
            return None
        return span_stack[-1]

    def _pop_span(self) -> Any | None:
        span_stack = self._span_stack_var.get()
        if not span_stack:
            return None
        span = span_stack[-1]
        self._span_stack_var.set(span_stack[:-1])
        return span
