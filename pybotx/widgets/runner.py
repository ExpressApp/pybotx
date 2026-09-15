import inspect
from collections.abc import Iterable
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import wraps
from time import perf_counter
from typing import TYPE_CHECKING, TypeVar, cast, overload

from pybotx.bot.bot import Bot
from pybotx.logger import logger
from pybotx.models.message.incoming_message import IncomingMessage

from .base import Widget

if TYPE_CHECKING:
    from .base import WidgetResultMode

W = TypeVar("W", bound=Widget)
T = TypeVar("T")


@dataclass(slots=True)
class RunnerHookResult:
    result: str | None = None
    should_display: bool = True
    widget: Widget | None = None


BeforeHookResult = RunnerHookResult | None | Awaitable[RunnerHookResult | None]
AfterHookResult = str | None | Awaitable[str | None]

RunnerBeforeHook = Callable[[W], BeforeHookResult]
RunnerAfterHook = Callable[[W], AfterHookResult]

RunnerHookResolverResult = (
    RunnerHookResult
    | str
    | None
    | Awaitable[RunnerHookResult | str | None]
)
RunnerHookResolver = Callable[[W], RunnerHookResolverResult]

ActionGetterResult = str | Awaitable[str]
ActionGetter = Callable[[W], ActionGetterResult]

ActionHookResult = (
    RunnerHookResult
    | str
    | None
    | Awaitable[RunnerHookResult | str | None]
)
ActionHook = Callable[[W], ActionHookResult]
ObserverHookResult = None | Awaitable[None]


@dataclass(frozen=True, slots=True)
class WidgetRunnerStartedEvent:
    message: IncomingMessage
    bot: Bot
    widget: Widget

    @property
    def widget_name(self) -> str:
        return type(self.widget).__name__

    @property
    def command(self) -> str:
        return self.widget.command

    @property
    def result_mode(self) -> "WidgetResultMode":
        return self.widget.result_mode


@dataclass(frozen=True, slots=True)
class WidgetRunnerFinishedEvent:
    message: IncomingMessage
    bot: Bot
    initial_widget: Widget
    widget: Widget
    duration_seconds: float
    displayed: bool
    skipped_by_before: bool
    before_results_sent: int
    after_results_sent: int
    error: Exception | None = None

    @property
    def initial_widget_name(self) -> str:
        return type(self.initial_widget).__name__

    @property
    def widget_name(self) -> str:
        return type(self.widget).__name__

    @property
    def command(self) -> str:
        return self.widget.command

    @property
    def result_mode(self) -> "WidgetResultMode":
        return self.widget.result_mode


class WidgetRunnerObserver:
    def on_started(self, event: WidgetRunnerStartedEvent) -> ObserverHookResult:
        return None

    def on_finished(self, event: WidgetRunnerFinishedEvent) -> ObserverHookResult:
        return None


@dataclass(frozen=True, slots=True)
class WidgetRunnerConfig:
    before_hooks: tuple[RunnerBeforeHook[Widget], ...] = ()
    after_hooks: tuple[RunnerAfterHook[Widget], ...] = ()
    observers: tuple[WidgetRunnerObserver, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "before_hooks", tuple(self.before_hooks))
        object.__setattr__(self, "after_hooks", tuple(self.after_hooks))
        object.__setattr__(self, "observers", tuple(self.observers))

    @classmethod
    def from_hooks(
        cls,
        *,
        before: RunnerBeforeHook[W] | None = None,
        after: RunnerAfterHook[W] | None = None,
        observers: Iterable[WidgetRunnerObserver] = (),
    ) -> "WidgetRunnerConfig":
        before_hooks: tuple[RunnerBeforeHook[Widget], ...]
        after_hooks: tuple[RunnerAfterHook[Widget], ...]
        before_hooks = () if before is None else (cast(RunnerBeforeHook[Widget], before),)
        after_hooks = () if after is None else (cast(RunnerAfterHook[Widget], after),)
        return cls(
            before_hooks=before_hooks,
            after_hooks=after_hooks,
            observers=tuple(observers),
        )

    def extend(
        self,
        *,
        before: RunnerBeforeHook[W] | None = None,
        after: RunnerAfterHook[W] | None = None,
        observers: Iterable[WidgetRunnerObserver] = (),
    ) -> "WidgetRunnerConfig":
        before_hooks = self.before_hooks
        after_hooks = self.after_hooks
        if before is not None:
            before_hooks += (cast(RunnerBeforeHook[Widget], before),)
        if after is not None:
            after_hooks += (cast(RunnerAfterHook[Widget], after),)
        return WidgetRunnerConfig(
            before_hooks=before_hooks,
            after_hooks=after_hooks,
            observers=self.observers + tuple(observers),
        )


@dataclass(frozen=True, slots=True)
class LoggingWidgetRunnerObserver(WidgetRunnerObserver):
    log_start: bool = False

    async def on_started(self, event: WidgetRunnerStartedEvent) -> None:
        if not self.log_start:
            return

        logger.bind(
            widget_name=event.widget_name,
            widget_command=event.command,
            widget_result_mode=event.result_mode,
        ).debug("Widget run started")

    async def on_finished(self, event: WidgetRunnerFinishedEvent) -> None:
        bound_logger = logger.bind(
            widget_name=event.widget_name,
            initial_widget_name=event.initial_widget_name,
            widget_command=event.command,
            widget_result_mode=event.result_mode,
            widget_displayed=event.displayed,
            widget_skipped_by_before=event.skipped_by_before,
            widget_before_results_sent=event.before_results_sent,
            widget_after_results_sent=event.after_results_sent,
            widget_duration_seconds=event.duration_seconds,
        )
        if event.error is None:
            bound_logger.info("Widget run finished")
            return

        bound_logger.opt(exception=event.error).warning("Widget run failed")


class WidgetRunner:
    def __init__(
        self,
        message: IncomingMessage,
        bot: Bot,
        *,
        config: WidgetRunnerConfig | None = None,
    ) -> None:
        self.message = message
        self.bot = bot
        self.config = config or WidgetRunnerConfig()

    async def run(
        self,
        *,
        widget: W,
        before: RunnerBeforeHook[W] | None = None,
        after: RunnerAfterHook[W] | None = None,
    ) -> None:
        initial_widget = widget
        before_hooks = self._build_before_hooks(before)
        after_hooks = self._build_after_hooks(after)
        started_event = WidgetRunnerStartedEvent(
            message=self.message,
            bot=self.bot,
            widget=initial_widget,
        )
        await self._notify_observers_started(started_event)

        displayed = False
        skipped_by_before = False
        before_results_sent = 0
        after_results_sent = 0
        started_at = perf_counter()
        try:
            for before_hook in before_hooks:
                before_result = await _resolve_awaitable(before_hook(widget))
                if before_result is None:
                    continue

                if before_result.widget is not None:
                    widget = cast(W, before_result.widget)

                if before_result.result is not None:
                    await widget.send_result(before_result.result)
                    before_results_sent += 1

                if not before_result.should_display:
                    skipped_by_before = True
                    break

            if not skipped_by_before:
                await widget.display()
                displayed = True

                for after_hook in after_hooks:
                    post_result = await _resolve_awaitable(after_hook(widget))
                    if post_result is None:
                        continue

                    await widget.send_result(post_result)
                    after_results_sent += 1
        except Exception as error:
            await self._notify_observers_finished(
                WidgetRunnerFinishedEvent(
                    message=self.message,
                    bot=self.bot,
                    initial_widget=initial_widget,
                    widget=widget,
                    duration_seconds=perf_counter() - started_at,
                    displayed=displayed,
                    skipped_by_before=skipped_by_before,
                    before_results_sent=before_results_sent,
                    after_results_sent=after_results_sent,
                    error=error,
                ),
            )
            raise

        await self._notify_observers_finished(
            WidgetRunnerFinishedEvent(
                message=self.message,
                bot=self.bot,
                initial_widget=initial_widget,
                widget=widget,
                duration_seconds=perf_counter() - started_at,
                displayed=displayed,
                skipped_by_before=skipped_by_before,
                before_results_sent=before_results_sent,
                after_results_sent=after_results_sent,
            ),
        )

    def _build_before_hooks(
        self,
        before: RunnerBeforeHook[W] | None,
    ) -> tuple[RunnerBeforeHook[W], ...]:
        hooks = tuple(cast(RunnerBeforeHook[W], hook) for hook in self.config.before_hooks)
        if before is not None:
            hooks += (before,)
        return hooks

    def _build_after_hooks(
        self,
        after: RunnerAfterHook[W] | None,
    ) -> tuple[RunnerAfterHook[W], ...]:
        hooks: tuple[RunnerAfterHook[W], ...] = ()
        if after is not None:
            hooks += (after,)
        hooks += tuple(cast(RunnerAfterHook[W], hook) for hook in self.config.after_hooks)
        return hooks

    async def _notify_observers_started(self, event: WidgetRunnerStartedEvent) -> None:
        for observer in self.config.observers:
            try:
                await _resolve_awaitable(observer.on_started(event))
            except Exception:
                logger.opt(exception=True).warning(
                    "Widget runner observer failed during start: {observer_name}",
                    observer_name=type(observer).__name__,
                )

    async def _notify_observers_finished(self, event: WidgetRunnerFinishedEvent) -> None:
        for observer in self.config.observers:
            try:
                await _resolve_awaitable(observer.on_finished(event))
            except Exception:
                logger.opt(exception=True).warning(
                    "Widget runner observer failed during finish: {observer_name}",
                    observer_name=type(observer).__name__,
                )


@overload
def widget_command(
    handler: Callable[[IncomingMessage, Bot], W | None | Awaitable[W | None]],
) -> Callable[[IncomingMessage, Bot], Awaitable[None]]:  # pragma: no cover
    ...


@overload
def widget_command(
    *,
    config: WidgetRunnerConfig,
) -> Callable[
    [Callable[[IncomingMessage, Bot], Widget | None | Awaitable[Widget | None]]],
    Callable[[IncomingMessage, Bot], Awaitable[None]],
]:  # pragma: no cover
    ...


@overload
def widget_command(
    handler: None = None,
    *,
    before: RunnerBeforeHook[W] | None = None,
    after: RunnerAfterHook[W] | None = None,
    config: WidgetRunnerConfig | None = None,
) -> Callable[
    [Callable[[IncomingMessage, Bot], W | None | Awaitable[W | None]]],
    Callable[[IncomingMessage, Bot], Awaitable[None]],
]:  # pragma: no cover
    ...


def widget_command(
    handler: Callable[[IncomingMessage, Bot], W | None | Awaitable[W | None]] | None = None,
    *,
    before: RunnerBeforeHook[W] | None = None,
    after: RunnerAfterHook[W] | None = None,
    config: WidgetRunnerConfig | None = None,
) -> (
    Callable[[IncomingMessage, Bot], Awaitable[None]]
    | Callable[
        [Callable[[IncomingMessage, Bot], W | None | Awaitable[W | None]]],
        Callable[[IncomingMessage, Bot], Awaitable[None]],
    ]
):
    def _decorator(
        wrapped_handler: Callable[[IncomingMessage, Bot], W | None | Awaitable[W | None]],
    ) -> Callable[[IncomingMessage, Bot], Awaitable[None]]:
        @wraps(wrapped_handler)
        async def _wrapped(message: IncomingMessage, bot: Bot) -> None:
            widget = await _resolve_awaitable(wrapped_handler(message, bot))
            if widget is None:
                return

            runner = WidgetRunner(message, bot, config=config)
            await runner.run(widget=widget, before=before, after=after)

        return _wrapped

    if handler is not None:
        return _decorator(handler)

    return _decorator


def on_data_key(
    key: str,
    resolver: RunnerHookResolver[W],
    *,
    should_display: bool = False,
) -> RunnerBeforeHook[W]:
    async def _hook(widget: W) -> RunnerHookResult | None:
        if key not in widget.message.data:
            return None

        resolved_result = await _resolve_awaitable(resolver(widget))
        return _normalize_before_hook_result(
            resolved_result,
            should_display=should_display,
        )

    return _hook


def on_completed(
    is_completed: Callable[[W], bool | Awaitable[bool]],
    resolver: Callable[[W], str | None | Awaitable[str | None]],
) -> RunnerAfterHook[W]:
    async def _hook(widget: W) -> str | None:
        completed = await _resolve_awaitable(is_completed(widget))
        if not completed:
            return None

        return await _resolve_awaitable(resolver(widget))

    return _hook


def on_action(
    get_action: ActionGetter[W],
    actions: dict[str, str | RunnerHookResult | ActionHook[W]],
    *,
    default: str | RunnerHookResult | ActionHook[W] | None = None,
    should_display: bool = False,
) -> RunnerBeforeHook[W]:
    async def _hook(widget: W) -> RunnerHookResult | None:
        try:
            action = await _resolve_awaitable(get_action(widget))
        except RuntimeError:
            return None

        resolver = actions.get(action, default)
        if resolver is None:
            return None

        if callable(resolver):
            resolved_result = await _resolve_awaitable(resolver(widget))
        else:
            resolved_result = resolver

        return _normalize_before_hook_result(
            resolved_result,
            should_display=should_display,
        )

    return _hook


def _normalize_before_hook_result(
    result: RunnerHookResult | str | None,
    *,
    should_display: bool,
) -> RunnerHookResult | None:
    if result is None or isinstance(result, RunnerHookResult):
        return result

    return RunnerHookResult(
        result=str(result),
        should_display=should_display,
    )


async def _resolve_awaitable(value: T | Awaitable[T]) -> T:
    if inspect.isawaitable(value):
        return await cast(Awaitable[T], value)
    return value
