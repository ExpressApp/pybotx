"""Lifespan mixin for bot."""

import asyncio
from typing import List, Set

from botx.concurrency import callable_to_coroutine
from botx.typing import BotLifespanEvent, Protocol


class LifespanEventsOwnerProtocol(Protocol):
    """Protocol for owner of lifespan events."""

    @property
    def startup_events(self) -> List[BotLifespanEvent]:
        """Startup events."""

    @property
    def shutdown_events(self) -> List[BotLifespanEvent]:
        """Shutdown events."""

    async def wait_current_handlers(self):
        """Wait for handlers shutdown."""


class LifespanMixin:
    """Lifespan events mixin for bot."""

    tasks: Set[asyncio.Future]

    async def start(self: LifespanEventsOwnerProtocol) -> None:
        """Run all startup events and other initialization stuff."""
        for event in self.startup_events:
            await callable_to_coroutine(event, self)

    async def shutdown(self: LifespanEventsOwnerProtocol) -> None:
        """Wait for all running handlers shutdown."""
        await self.wait_current_handlers()

        for event in self.shutdown_events:
            await callable_to_coroutine(event, self)

    async def wait_current_handlers(self) -> None:
        """Wait until all current tasks are done."""
        if self.tasks:
            tasks, _ = await asyncio.wait(
                self.tasks, return_when=asyncio.ALL_COMPLETED,
            )
            for task in tasks:
                task.result()

        self.tasks.clear()
