from typing import cast

import pytest

from pybotx.widgets import (
    LoggingWidgetRunnerObserver,
    PrometheusWidgetRunnerMetricsCollector,
    RunnerHookResult,
    WidgetRunnerConfig,
    WidgetRunnerObservabilityPreset,
    WidgetRunnerObserver,
    WidgetRunnerPreset,
    build_production_widget_runner_preset,
    build_widget_runner_observability_preset,
)
from pybotx.widgets.base import Widget


def test__build_widget_runner_observability_preset__adds_logging_observer() -> None:
    preset = build_widget_runner_observability_preset()

    assert isinstance(preset, WidgetRunnerObservabilityPreset)
    assert len(preset.observers) == 1
    assert isinstance(preset.observers[0], LoggingWidgetRunnerObserver)
    assert preset.as_config() == WidgetRunnerConfig(observers=preset.observers)


def test__build_widget_runner_observability_preset__supports_custom_observers() -> None:
    class _CustomObserver(WidgetRunnerObserver):
        def on_started(self, _event: object) -> None:
            return None

        def on_finished(self, _event: object) -> None:
            return None

    custom_observer = _CustomObserver()

    preset = build_widget_runner_observability_preset(
        observers=(custom_observer,),
    )

    assert preset.observers[1] is custom_observer


def test__build_widget_runner_observability_preset__requires_at_least_one_observer() -> None:
    with pytest.raises(ValueError):
        build_widget_runner_observability_preset(enable_logging_observer=False)


def test__build_widget_runner_observability_preset__supports_prometheus_metrics() -> None:
    prometheus_client = pytest.importorskip("prometheus_client")
    registry = prometheus_client.CollectorRegistry()

    preset = build_widget_runner_observability_preset(
        enable_logging_observer=False,
        enable_prometheus_metrics=True,
        registry=registry,
    )

    assert len(preset.observers) == 1
    assert isinstance(preset.observers[0], PrometheusWidgetRunnerMetricsCollector)


def test__build_production_widget_runner_preset__builds_runner_config() -> None:
    calls: list[str] = []

    def _before(_: Widget) -> RunnerHookResult:
        calls.append("before")
        return RunnerHookResult(result="before", should_display=True)

    def _after(_: Widget) -> str | None:
        calls.append("after")
        return "after"

    preset = build_production_widget_runner_preset(
        before=_before,
        after=_after,
    )

    assert isinstance(preset, WidgetRunnerPreset)
    assert preset.as_runner_kwargs() == {"config": preset.config}
    assert preset.as_config() is preset.config
    assert preset.as_widget_command_kwargs() == {"config": preset.config}
    assert len(preset.config.before_hooks) == 1
    assert len(preset.config.after_hooks) == 1
    assert len(preset.config.observers) == 1
    assert isinstance(preset.config.observers[0], LoggingWidgetRunnerObserver)

    widget = cast(Widget, object())
    before_result = preset.config.before_hooks[0](widget)
    after_result = preset.config.after_hooks[0](widget)

    assert isinstance(before_result, RunnerHookResult)
    assert before_result.result == "before"
    assert after_result == "after"
    assert calls == ["before", "after"]


def test__build_production_widget_runner_preset__extends_with_extra_hooks() -> None:
    order: list[str] = []

    def _before_one(_: Widget) -> RunnerHookResult:
        order.append("before_one")
        return RunnerHookResult()

    def _before_two(_: Widget) -> RunnerHookResult:
        order.append("before_two")
        return RunnerHookResult()

    def _after_one(_: Widget) -> str | None:
        order.append("after_one")
        return None

    def _after_two(_: Widget) -> str | None:
        order.append("after_two")
        return None

    preset = build_production_widget_runner_preset(
        before=_before_one,
        before_hooks=(_before_two,),
        after=_after_one,
        after_hooks=(_after_two,),
        observability_preset=WidgetRunnerObservabilityPreset(observers=()),
    )

    widget = cast(Widget, object())
    for before_hook in preset.config.before_hooks:
        before_hook(widget)
    for after_hook in preset.config.after_hooks:
        after_hook(widget)

    assert order == ["before_one", "before_two", "after_one", "after_two"]


def test__build_production_widget_runner_preset__uses_custom_observability_preset() -> None:
    class _CustomObserver(WidgetRunnerObserver):
        def on_started(self, _event: object) -> None:
            return None

        def on_finished(self, _event: object) -> None:
            return None

    custom_observer = _CustomObserver()
    observability_preset = WidgetRunnerObservabilityPreset(observers=(custom_observer,))

    preset = build_production_widget_runner_preset(
        observability_preset=observability_preset,
    )

    assert preset.config.observers == (custom_observer,)
