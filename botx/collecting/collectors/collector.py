"""Definition for collector."""
from typing import Any, Optional, Sequence

from loguru import logger
from pydantic.dataclasses import dataclass

from botx.collecting.collectors.base import BaseCollector
from botx.collecting.collectors.mixins.default import DefaultHandlerMixin
from botx.collecting.collectors.mixins.handler import HandlerMixin
from botx.collecting.collectors.mixins.hidden import HiddenHandlerMixin
from botx.collecting.collectors.mixins.system_events import SystemEventsHandlerMixin
from botx.dependencies.models import Depends
from botx.exceptions import NoMatchFound
from botx.models.messages.message import Message


@dataclass
class Collector(  # noqa: WPS215
    HandlerMixin,
    DefaultHandlerMixin,
    HiddenHandlerMixin,
    SystemEventsHandlerMixin,
    BaseCollector,
):
    """Collector for different handlers."""

    async def __call__(self, message: Message) -> None:
        """Find handler and execute it.

        Arguments:
            message: incoming message that will be passed to handler.
        """
        await self.handle_message(message)

    def include_collector(
        self,
        collector: "Collector",
        *,
        dependencies: Optional[Sequence[Depends]] = None,
    ) -> None:
        """Include handlers from another collector into this one.

        Arguments:
            collector: collector from which handlers should be copied.
            dependencies: optional sequence of dependencies for handlers for this
                collector.

        Raises:
            AssertionError: raised if both collectors defines default handlers.
        """
        if self.default_message_handler and collector.default_message_handler:
            raise AssertionError("only one default handler can be applied")

        if collector.default_message_handler:
            self._add_default_handler(collector.default_message_handler, dependencies)

        self._add_handlers(collector.handlers, dependencies)

    def command_for(self, *args: Any) -> str:
        """Find handler and build a command string using passed body query_params.

        Arguments:
            args: sequence of elements where first element should be name of handler.

        Returns:
            Command string.

        Raises:
            TypeError: raised no arguments passed.
        """
        if not len(args):
            raise TypeError("missing handler name as the first argument")

        return self.handler_for(args[0]).command_for(*args)

    async def handle_message(self, message: Message) -> None:
        """Find handler and execute it.

        Arguments:
            message: incoming message that will be passed to handler.

        Raises:
            NoMatchFound: raised if no handler for message found.
        """
        for handler in self.sorted_handlers:
            if handler.matches(message):
                logger.bind(botx_collector=True).info(
                    "botx => {0}: {1}".format(handler.name, message.command.command),
                )
                await handler(message)
                return

        if self.default_message_handler:
            await self.default_message_handler(message)
        else:
            raise NoMatchFound(search_param=message.body)
