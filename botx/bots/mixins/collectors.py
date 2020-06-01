"""Definition for bot's collecting component.

All of this methods are just wrappers around inner collector.
"""

from typing import Any, List, Optional, Sequence

from botx.bots.mixins.collecting.add_handler import AddHandlerMixin
from botx.bots.mixins.collecting.default import DefaultHandlerMixin
from botx.bots.mixins.collecting.handler import HandlerMixin
from botx.bots.mixins.collecting.hidden import HiddenHandlerMixin
from botx.bots.mixins.collecting.system_events import SystemEventsHandlerMixin
from botx.collecting.collectors.collector import Collector
from botx.collecting.handlers.handler import Handler
from botx.dependencies import models as deps


class BotCollectingMixin(  # noqa: WPS215
    AddHandlerMixin,
    HandlerMixin,
    DefaultHandlerMixin,
    HiddenHandlerMixin,
    SystemEventsHandlerMixin,
):
    """Mixin that defines collector-like behaviour."""

    collector: Collector

    @property
    def handlers(self) -> List[Handler]:
        """Get handlers registered on this bot.

        Returns:
            Registered handlers of bot.
        """
        return self.collector.handlers

    def include_collector(
        self,
        collector: Collector,
        *,
        dependencies: Optional[Sequence[deps.Depends]] = None,
    ) -> None:
        """Include handlers from collector into bot.

        Arguments:
            collector: collector from which handlers should be copied.
            dependencies: optional sequence of dependencies for handlers for this
                collector.
        """
        self.collector.include_collector(collector, dependencies=dependencies)

    def command_for(self, *args: Any) -> str:
        """Find handler and build a command string using passed body query_params.

        Arguments:
            args: sequence of elements where first element should be name of handler.

        Returns:
            Command string.
        """
        return self.collector.command_for(*args)

    def handler_for(self, name: str) -> Handler:
        """Find handler in handlers of this bot.

        Find registered handler using using [botx.collector.Collector.handler_for] of
        inner collector.

        Arguments:
            name: name of handler that should be found.

        Returns:
            Handler that was found by name.
        """
        return self.collector.handler_for(name)
