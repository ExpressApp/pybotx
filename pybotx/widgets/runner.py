import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import wraps
from typing import TypeVar, cast, overload

from pybotx.bot.bot import Bot
from pybotx.models.message.incoming_message import IncomingMessage

from .base import Widget

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


class WidgetRunner:
    def __init__(self, message: IncomingMessage, bot: Bot) -> None:
        self.message = message
        self.bot = bot

    async def run(
        self,
        *,
        widget: W,
        before: RunnerBeforeHook[W] | None = None,
        after: RunnerAfterHook[W] | None = None,
    ) -> None:
        if before is not None:
            before_result = await _resolve_awaitable(before(widget))
            if before_result is not None:
                if before_result.widget is not None:
                    widget = cast(W, before_result.widget)

                if before_result.result is not None:
                    await widget.send_result(before_result.result)

                if not before_result.should_display:
                    return

        await widget.display()

        if after is not None:
            post_result = await _resolve_awaitable(after(widget))
            if post_result is not None:
                await widget.send_result(post_result)


@overload
def widget_command(
    handler: Callable[[IncomingMessage, Bot], W | None | Awaitable[W | None]],
) -> Callable[[IncomingMessage, Bot], Awaitable[None]]:
    ...


@overload
def widget_command(
    *,
    before: RunnerBeforeHook[W] | None = None,
    after: RunnerAfterHook[W] | None = None,
) -> Callable[
    [Callable[[IncomingMessage, Bot], W | None | Awaitable[W | None]]],
    Callable[[IncomingMessage, Bot], Awaitable[None]],
]:
    ...


def widget_command(
    handler: Callable[[IncomingMessage, Bot], W | None | Awaitable[W | None]] | None = None,
    *,
    before: RunnerBeforeHook[W] | None = None,
    after: RunnerAfterHook[W] | None = None,
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

            runner = WidgetRunner(message, bot)
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
