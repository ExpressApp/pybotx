import inspect
import logging
from typing import TYPE_CHECKING, Any, Dict, Union

import aiojobs
from botx.core import BotXException
from botx.types import Message, RequestTypeEnum, Status

from .base_dispatcher import BaseDispatcher
from .command_handler import CommandHandler

if TYPE_CHECKING:
    from botx.bot.async_bot import AsyncBot  # pylint: disable=cyclic-import

LOGGER = logging.getLogger("botx")


class AsyncDispatcher(BaseDispatcher):
    _scheduler = aiojobs.Scheduler
    _bot: "AsyncBot"

    async def start(self):
        self._scheduler = await aiojobs.create_scheduler()

    async def shutdown(self):
        await self._scheduler.close()

    async def parse_request(
        self, data: Dict[str, Any], request_type: Union[str, RequestTypeEnum]
    ) -> Union[Status, bool]:
        if request_type == RequestTypeEnum.status:
            return self._create_status()

        if request_type == RequestTypeEnum.command:
            return await self._create_message(data)

        raise BotXException(f"wrong request type {request_type !r}")

    async def _create_message(self, data: Dict[str, Any]) -> bool:
        message = Message(**data)
        LOGGER.debug("message created: %r", message.json())

        cmd = message.command.cmd
        command = self._handlers.get(cmd)
        if command:
            LOGGER.debug("spawning command %r ", cmd)
            await self._scheduler.spawn(command.func(message, self._bot))
            return True

        LOGGER.debug("no command %r found", cmd)
        if self._default_handler:
            LOGGER.debug("spawning default handler")
            job = await self._scheduler.spawn(
                self._default_handler.func(message, self._bot)
            )
            print(job)
            return True

        LOGGER.debug("default handler was not set")
        return False

    def add_handler(self, handler: CommandHandler):
        if not inspect.iscoroutinefunction(handler.func):
            raise BotXException("can not add not async handler to async dispatcher")

        super().add_handler(handler)
