import aiojobs
import inspect
from typing import Any, Dict, NoReturn, Union

from botx.core import BotXException
from botx.types import Message, RequestTypeEnum, Status, SyncID
from .basedispatcher import BaseDispatcher
from .commandhandler import CommandHandler


class AsyncDispatcher(BaseDispatcher):
    _scheduler = aiojobs.Scheduler

    def __init__(self):
        super().__init__()

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

    async def _create_message(self, data: Dict[str, Any]) -> bool:
        message = Message(**data)
        message.sync_id = SyncID(str(message.sync_id))

        cmd = message.command.cmd
        command = self._handlers.get(cmd)
        if command:
            await self._scheduler.spawn(command.func(message))
            return True
        else:
            if self._default_handler:
                await self._scheduler.spawn(self._default_handler.func(message))
                return True
        return False

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        if not inspect.iscoroutinefunction(handler.func):
            raise BotXException("can not add not async handler to async dispatcher")

        super().add_handler(handler)
