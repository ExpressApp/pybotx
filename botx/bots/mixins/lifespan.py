"""Lifespan mixin for bot."""

import asyncio
from typing import List, Set

from botx.concurrency import callable_to_coroutine
from botx.typing import BotLifespanEvent

try:
    from typing import Protocol  # noqa: WPS433
except ImportError:
    from typing_extensions import Protocol  # type: ignore  # noqa: WPS433, WPS440, F401


class LifespanMixin:
    """Lifespan events mixin for bot."""

    #: currently running tasks.
    tasks: Set[asyncio.Future]

    #: startup events.
    startup_events: List[BotLifespanEvent]

    #: shutdown events.
    shutdown_events: List[BotLifespanEvent]

    async def start(self) -> None:
        """Run all startup events and other initialization stuff."""
        for event in self.startup_events:
            await callable_to_coroutine(event, self)

    async def shutdown(self) -> None:
        """Wait for all running handlers shutdown."""
        await self.wait_current_handlers()

        for event in self.shutdown_events:
            await callable_to_coroutine(event, self)

    async def wait_current_handlers(self) -> None:
        """Wait until all current tasks are done."""
        if self.tasks:
            tasks, _ = await asyncio.wait(
                self.tasks,
                return_when=asyncio.ALL_COMPLETED,
            )
            for task in tasks:
                task.result()

        self.tasks.clear()
