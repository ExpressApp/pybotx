import inspect
import logging
from typing import Any, Dict, NoReturn, Union

import aiojobs

from botx.core import BotXException
from botx.types import Message, RequestTypeEnum, Status

from .basedispatcher import BaseDispatcher
from .commandhandler import CommandHandler

LOGGER = logging.getLogger("botx")


class AsyncDispatcher(BaseDispatcher):
    _scheduler = aiojobs.Scheduler
    _bot: "AsyncBot"

    def __init__(self, bot):
        super().__init__(bot)

    async def start(self) -> NoReturn:
        self._scheduler = await aiojobs.create_scheduler()

    async def shutdown(self) -> NoReturn:
        await self._scheduler.close()

    async def parse_request(
        self, data: Dict[str, Any], request_type: Union[str, RequestTypeEnum]
    ) -> Union[Status, bool]:
        if request_type == RequestTypeEnum.status:
            return self._create_status()
        elif request_type == RequestTypeEnum.command:
            return await self._create_message(data)
        else:
            raise BotXException(f"wrong request type {request_type !r}")

    async def _create_message(self, data: Dict[str, Any]) -> bool:
        message = Message(**data)
        LOGGER.debug(f"message created: {message.json() !r}")

        cmd = message.command.cmd
        command = self._handlers.get(cmd)
        if command:
            LOGGER.debug(f"spawning command {cmd !r}")
            await self._scheduler.spawn(command.func(message, self._bot))
            return True
        else:
            LOGGER.debug(f"no command {cmd !r} found")
            if self._default_handler:
                LOGGER.debug("spawning default handler")
                job = await self._scheduler.spawn(
                    self._default_handler.func(message, self._bot)
                )
                print(job)
                return True

        LOGGER.debug("default handler was not set")
        return False

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        if not inspect.iscoroutinefunction(handler.func):
            raise BotXException("can not add not async handler to async dispatcher")

        super().add_handler(handler)
