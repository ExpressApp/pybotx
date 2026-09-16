from pybotx.widgets import (
    ApprovalWidget,
    AsyncJobWidget,
    BatchFileItem,
    build_production_widget_runner_preset,
    build_widget_runner_observability_preset,
    CalendarWidget,
    CarouselWidget,
    CheckListWidget,
    CheckboxContent,
    ChecktableWidget,
    ConfirmWidget,
    DateRangeWidget,
    FileBatchWidget,
    FormWizardStep,
    FormWizardWidget,
    InMemoryWidgetRunnerMetricsCollector,
    LoggingWidgetRunnerObserver,
    MessageMarkup,
    MessagesPagerWidget,
    MultiSelectWidget,
    NoopWidgetRunnerMetricsCollector,
    PaginationWidget,
    PrometheusWidgetRunnerMetricsCollector,
    RangeWidget,
    RunnerHookResult,
    SearchSelectWidget,
    SelectOption,
    SelectWidget,
    TableWidget,
    Undefined,
    WidgetRunner,
    WidgetRunnerConfig,
    WidgetRunnerFinishedEvent,
    WidgetRunnerMetricsSnapshot,
    WidgetRunnerObserver,
    WidgetRunnerObservabilityPreset,
    WidgetRunnerPreset,
    WidgetRunnerStartedEvent,
    on_action,
    on_completed,
    on_data_key,
    widget_command,
    undefined,
)


def test__widgets_module__exports() -> None:
    assert CalendarWidget is not None
    assert CarouselWidget is not None
    assert ApprovalWidget is not None
    assert AsyncJobWidget is not None
    assert BatchFileItem is not None
    assert CheckListWidget is not None
    assert ChecktableWidget is not None
    assert CheckboxContent is not None
    assert ConfirmWidget is not None
    assert DateRangeWidget is not None
    assert FileBatchWidget is not None
    assert FormWizardStep is not None
    assert FormWizardWidget is not None
    assert InMemoryWidgetRunnerMetricsCollector is not None
    assert MessageMarkup is not None
    assert MessagesPagerWidget is not None
    assert MultiSelectWidget is not None
    assert NoopWidgetRunnerMetricsCollector is not None
    assert PaginationWidget is not None
    assert PrometheusWidgetRunnerMetricsCollector is not None
    assert RangeWidget is not None
    assert LoggingWidgetRunnerObserver is not None
    assert RunnerHookResult is not None
    assert SearchSelectWidget is not None
    assert SelectOption is not None
    assert SelectWidget is not None
    assert TableWidget is not None
    assert WidgetRunner is not None
    assert WidgetRunnerConfig is not None
    assert WidgetRunnerFinishedEvent is not None
    assert WidgetRunnerMetricsSnapshot is not None
    assert WidgetRunnerObserver is not None
    assert WidgetRunnerObservabilityPreset is not None
    assert WidgetRunnerPreset is not None
    assert WidgetRunnerStartedEvent is not None
    assert build_production_widget_runner_preset is not None
    assert build_widget_runner_observability_preset is not None
    assert on_action is not None
    assert on_completed is not None
    assert on_data_key is not None
    assert widget_command is not None
    assert Undefined is not None
    assert undefined is not None


def test__widgets_module__undefined_singleton() -> None:
    assert Undefined() is undefined
