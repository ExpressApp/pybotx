from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, TypeVar

from pybotx.widgets.base import Widget
from pybotx.widgets.observability import PrometheusWidgetRunnerMetricsCollector
from pybotx.widgets.runner import (
    LoggingWidgetRunnerObserver,
    RunnerAfterHook,
    RunnerBeforeHook,
    WidgetRunnerConfig,
    WidgetRunnerObserver,
)

W = TypeVar("W", bound=Widget)


@dataclass(frozen=True, slots=True)
class WidgetRunnerObservabilityPreset:
    observers: tuple[WidgetRunnerObserver, ...]

    def as_config(self) -> WidgetRunnerConfig:
        return WidgetRunnerConfig(observers=self.observers)


@dataclass(frozen=True, slots=True)
class WidgetRunnerPreset:
    config: WidgetRunnerConfig

    def as_config(self) -> WidgetRunnerConfig:
        return self.config

    def as_runner_kwargs(self) -> dict[str, object]:
        return {"config": self.config}

    def as_widget_command_kwargs(self) -> dict[str, object]:
        return {"config": self.config}


def build_widget_runner_observability_preset(
    *,
    enable_logging_observer: bool = True,
    enable_prometheus_metrics: bool = False,
    log_start: bool = False,
    registry: Any | None = None,
    metric_prefix: str = "pybotx_widget",
    latency_buckets: tuple[float, ...] | None = None,
    observers: Iterable[WidgetRunnerObserver] = (),
) -> WidgetRunnerObservabilityPreset:
    configured_observers = tuple(observers)
    if enable_logging_observer:
        configured_observers = (
            LoggingWidgetRunnerObserver(log_start=log_start),
            *configured_observers,
        )
    if enable_prometheus_metrics:
        configured_observers = (
            *configured_observers,
            PrometheusWidgetRunnerMetricsCollector(
                registry=registry,
                metric_prefix=metric_prefix,
                latency_buckets=latency_buckets,
            ),
        )

    if not configured_observers:
        raise ValueError(
            "At least one widget runner observer should be enabled",
        )

    return WidgetRunnerObservabilityPreset(observers=configured_observers)


def build_production_widget_runner_preset(
    *,
    before: RunnerBeforeHook[W] | None = None,
    after: RunnerAfterHook[W] | None = None,
    before_hooks: Iterable[RunnerBeforeHook[W]] = (),
    after_hooks: Iterable[RunnerAfterHook[W]] = (),
    observability_preset: WidgetRunnerObservabilityPreset | None = None,
) -> WidgetRunnerPreset:
    config = WidgetRunnerConfig.from_hooks(before=before, after=after)

    for before_hook in before_hooks:
        config = config.extend(
            before=before_hook,
        )

    for after_hook in after_hooks:
        config = config.extend(
            after=after_hook,
        )

    if observability_preset is None:
        observability_preset = build_widget_runner_observability_preset()

    config = config.extend(observers=observability_preset.observers)

    return WidgetRunnerPreset(config=config)
