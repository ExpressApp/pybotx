import importlib
from dataclasses import dataclass
from typing import Any

import pytest

from pybotx import (
    BotXOperation,
    BotXRequestMetadata,
    BotXRetryRequestPolicy,
    build_production_bot_preset,
    build_production_observability_preset,
    build_production_retry_preset,
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

    def set_attribute(self, _key: str, _value: object) -> None:
        return None

    def add_event(self, _name: str, attributes: dict[str, object] | None = None) -> None:
        return None

    def record_exception(self, _exc: Exception) -> None:
        return None

    def set_status(self, _status: _FakeStatus) -> None:
        return None

    def end(self) -> None:
        return None


class _FakeTracer:
    def start_span(self, name: str, kind: str | None = None) -> _FakeSpan:
        return _FakeSpan(name, kind)


class _FakeTraceAPI:
    Status = _FakeStatus
    StatusCode = _FakeStatusCode
    SpanKind = _FakeSpanKind

    def __init__(self) -> None:
        self._tracer = _FakeTracer()

    def get_tracer(self, *_args: object, **_kwargs: object) -> _FakeTracer:
        return self._tracer


def test__build_production_retry_preset__builds_retry_kwargs_and_safe_policy() -> None:
    preset = build_production_retry_preset(max_attempts=5)

    kwargs = preset.as_bot_kwargs()
    retry_request_policy = kwargs["retry_request_policy"]
    assert hasattr(retry_request_policy, "should_retry")
    assert kwargs["retry_policy"] == preset.retry_policy
    assert preset.retry_policy.max_attempts == 5
    assert retry_request_policy.should_retry(
        BotXRequestMetadata(
            method="GET",
            url="https://cts.example.com/api/v4/botx/chats/info",
        ),
    )
    assert retry_request_policy.should_retry(
        BotXRequestMetadata(
            method="POST",
            url="https://cts.example.com/api/v4/botx/users/search",
            operation_name=BotXOperation.SEARCH_USER_BY_EMAILS,
        ),
    )
    assert not retry_request_policy.should_retry(
        BotXRequestMetadata(
            method="POST",
            url="https://cts.example.com/api/v4/botx/notifications/direct",
            operation_name=BotXOperation.DIRECT_NOTIFICATION,
        ),
    )


def test__build_production_retry_preset__supports_extra_safe_operations() -> None:
    preset = build_production_retry_preset(extra_safe_operations={"CustomReadOnlyMethod"})

    assert preset.retry_request_policy.should_retry(
        BotXRequestMetadata(
            method="POST",
            url="https://cts.example.com/custom/read-only",
            operation_name="CustomReadOnlyMethod",
        ),
    )


def test__build_production_retry_preset__rejects_mixed_custom_request_policy_and_extras() -> None:
    class _RetryAllPolicy(BotXRetryRequestPolicy):
        def should_retry(self, metadata: Any) -> bool:
            return True

    with pytest.raises(ValueError):
        build_production_retry_preset(
            retry_request_policy=_RetryAllPolicy(),
            extra_safe_operations={"CustomReadOnlyMethod"},
        )


def test__build_production_observability_preset__requires_at_least_one_backend() -> None:
    with pytest.raises(ValueError):
        build_production_observability_preset(
            enable_prometheus_metrics=False,
            enable_open_telemetry_tracing=False,
        )


def test__build_production_observability_preset__builds_prometheus_metrics_only() -> None:
    prometheus_client = pytest.importorskip("prometheus_client")
    registry = prometheus_client.CollectorRegistry()

    preset = build_production_observability_preset(
        enable_open_telemetry_tracing=False,
        registry=registry,
    )

    kwargs = preset.as_bot_kwargs()
    assert "metrics_collector" in kwargs
    assert "ingress_metrics_collector" in kwargs
    assert "tracing_collector" not in kwargs


def test__build_production_observability_preset__builds_tracing_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trace_api = _FakeTraceAPI()
    original_import_module = importlib.import_module

    def import_module(name: str) -> object:
        if name == "opentelemetry.trace":
            return trace_api
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", import_module)

    preset = build_production_observability_preset(
        enable_prometheus_metrics=False,
        tracer_name="tests.pybotx",
    )

    kwargs = preset.as_bot_kwargs()
    assert "metrics_collector" not in kwargs
    assert "ingress_metrics_collector" not in kwargs
    assert "tracing_collector" in kwargs


def test__build_production_bot_preset__combines_retry_and_observability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prometheus_client = pytest.importorskip("prometheus_client")
    trace_api = _FakeTraceAPI()
    original_import_module = importlib.import_module

    def import_module(name: str) -> object:
        if name == "opentelemetry.trace":
            return trace_api
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", import_module)
    registry = prometheus_client.CollectorRegistry()

    preset = build_production_bot_preset(
        retry_preset=build_production_retry_preset(),
        observability_preset=build_production_observability_preset(registry=registry),
    )

    kwargs = preset.as_bot_kwargs()
    assert "retry_policy" in kwargs
    assert "retry_request_policy" in kwargs
    assert "metrics_collector" in kwargs
    assert "tracing_collector" in kwargs
    assert "ingress_metrics_collector" in kwargs


def test__build_production_bot_preset__default_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("prometheus_client")
    trace_api = _FakeTraceAPI()
    original_import_module = importlib.import_module

    def import_module(name: str) -> object:
        if name == "opentelemetry.trace":
            return trace_api
        return original_import_module(name)

    monkeypatch.setattr(importlib, "import_module", import_module)

    preset = build_production_bot_preset()

    kwargs = preset.as_bot_kwargs()
    assert "retry_policy" in kwargs
    assert "retry_request_policy" in kwargs
    assert "metrics_collector" in kwargs
    assert "tracing_collector" in kwargs
    assert "ingress_metrics_collector" in kwargs
