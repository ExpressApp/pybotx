import importlib
from dataclasses import dataclass

import pytest

from pybotx import (
    BotXRequestMetadata,
    BotXRequestResult,
    BotXRetryEvent,
    OpenTelemetryTracingCollector,
)


@dataclass
class _FakeStatus:
    status_code: str
    description: str | None = None


class _FakeStatusCode:
    OK = "OK"
    ERROR = "ERROR"


class _FakeSpanKind:
    CLIENT = "CLIENT"


class _FakeSpan:
    def __init__(self, name: str, kind: str | None = None) -> None:
        self.name = name
        self.kind = kind
        self.attributes: dict[str, object] = {}
        self.events: list[tuple[str, dict[str, object]]] = []
        self.exceptions: list[Exception] = []
        self.status: _FakeStatus | None = None
        self.ended = False

    def set_attribute(self, key: str, value: object) -> None:
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict[str, object] | None = None) -> None:
        self.events.append((name, attributes or {}))

    def record_exception(self, exc: Exception) -> None:
        self.exceptions.append(exc)

    def set_status(self, status: _FakeStatus) -> None:
        self.status = status

    def end(self) -> None:
        self.ended = True


class _FakeTracer:
    def __init__(self) -> None:
        self.spans: list[_FakeSpan] = []

    def start_span(self, name: str, kind: str | None = None) -> _FakeSpan:
        span = _FakeSpan(name, kind)
        self.spans.append(span)
        return span


class _FakeTraceAPI:
    Status = _FakeStatus
    StatusCode = _FakeStatusCode
    SpanKind = _FakeSpanKind

    def __init__(self, tracer: _FakeTracer) -> None:
        self._tracer = tracer

    def get_tracer(self, *_args: object, **_kwargs: object) -> _FakeTracer:
        return self._tracer


def test__open_telemetry_tracing_collector__creates_span_and_retry_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # - Arrange -
    tracer = _FakeTracer()
    trace_api = _FakeTraceAPI(tracer)
    original_import_module = importlib.import_module

    def import_module(name: str) -> object:
        if name == "opentelemetry.trace":
            return trace_api
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", import_module)
    collector = OpenTelemetryTracingCollector()
    metadata = BotXRequestMetadata(
        method="POST",
        url="https://cts.example.com:8443/api/v4/botx/notifications/internal",
    )

    # - Act -
    collector.on_request_start(metadata)
    collector.on_request_retry(
        metadata,
        BotXRetryEvent(
            attempt=1,
            max_attempts=3,
            sleep_seconds=0.2,
            reason="status_code=503",
        ),
    )
    collector.on_request_finish(
        metadata,
        BotXRequestResult(status_code=200, duration_ms=125),
    )

    # - Assert -
    assert len(tracer.spans) == 1
    span = tracer.spans[0]
    assert span.name == "POST /api/v4/botx/notifications/internal"
    assert span.kind == _FakeSpanKind.CLIENT
    assert span.attributes["http.method"] == "POST"
    assert span.attributes["http.url"] == metadata.url
    assert span.attributes["http.target"] == "/api/v4/botx/notifications/internal"
    assert span.attributes["server.address"] == "cts.example.com"
    assert span.attributes["server.port"] == 8443
    assert span.attributes["http.status_code"] == 200
    assert span.attributes["botx.duration_ms"] == 125
    assert span.events == [
        (
            "botx.retry",
            {
                "retry.attempt": 1,
                "retry.max_attempts": 3,
                "retry.sleep_seconds": 0.2,
                "retry.reason": "status_code=503",
                "http.method": "POST",
            },
        ),
    ]
    assert span.status is not None
    assert span.status.status_code == _FakeStatusCode.OK
    assert span.ended is True


def test__open_telemetry_tracing_collector__supports_span_enricher(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # - Arrange -
    tracer = _FakeTracer()
    trace_api = _FakeTraceAPI(tracer)
    original_import_module = importlib.import_module

    def import_module(name: str) -> object:
        if name == "opentelemetry.trace":
            return trace_api
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", import_module)

    def span_enricher(span: _FakeSpan, metadata: BotXRequestMetadata) -> None:
        span.set_attribute("botx.custom.enriched", True)
        span.set_attribute("botx.custom.method", metadata.method)

    collector = OpenTelemetryTracingCollector(span_enricher=span_enricher)
    metadata = BotXRequestMetadata(
        method="DELETE",
        url="https://cts.example.com/api/v3/botx/chats/remove_user",
    )

    # - Act -
    collector.on_request_start(metadata)
    collector.on_request_finish(
        metadata,
        BotXRequestResult(status_code=200, duration_ms=10),
    )

    # - Assert -
    span = tracer.spans[0]
    assert span.attributes["botx.custom.enriched"] is True
    assert span.attributes["botx.custom.method"] == "DELETE"


def test__open_telemetry_tracing_collector__records_error_in_span(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # - Arrange -
    tracer = _FakeTracer()
    trace_api = _FakeTraceAPI(tracer)
    original_import_module = importlib.import_module

    def import_module(name: str) -> object:
        if name == "opentelemetry.trace":
            return trace_api
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", import_module)
    collector = OpenTelemetryTracingCollector()
    metadata = BotXRequestMetadata(
        method="GET",
        url="https://cts.example.com/api/v2/botx/bots/token",
    )
    error = RuntimeError("boom")

    # - Act -
    collector.on_request_start(metadata)
    collector.on_request_finish(
        metadata,
        BotXRequestResult(status_code=None, duration_ms=31, error=error),
    )

    # - Assert -
    span = tracer.spans[0]
    assert span.exceptions == [error]
    assert span.status is not None
    assert span.status.status_code == _FakeStatusCode.ERROR
    assert span.status.description == "boom"
    assert span.ended is True


def test__open_telemetry_tracing_collector__requires_opentelemetry_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # - Arrange -
    original_import_module = importlib.import_module

    def import_module(name: str) -> object:
        if name == "opentelemetry.trace":
            raise ModuleNotFoundError(name)
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", import_module)

    # - Act / Assert -
    with pytest.raises(RuntimeError, match="opentelemetry-api"):
        OpenTelemetryTracingCollector()
