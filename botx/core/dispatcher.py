from collections import OrderedDict

import abc
import aiojobs
import inspect
from concurrent.futures.thread import ThreadPoolExecutor
from enum import Enum
from typing import Any, Awaitable, Dict, NoReturn, Optional, Union

from botx.exception import BotXException
from botx.types import Message, Status, StatusResult, SyncID
from .commandhandler import CommandHandler


class RequestTypeEnum(str, Enum):
    status: str = "status"
    command: str = "command"


class BaseDispatcher(abc.ABC):
    _handlers: Dict[str, CommandHandler]
    _default_handler: Optional[CommandHandler] = None

    def __init__(self):
        self._handlers = OrderedDict()

    @abc.abstractmethod
    def start(self) -> NoReturn:  # pragma: no cover
        pass

    @abc.abstractmethod
    def shutdown(self) -> NoReturn:  # pragma: no cover
        pass

    @abc.abstractmethod
    def parse_request(
        self, data: Dict[str, Any], request_type: Union[str, RequestTypeEnum]
    ) -> Union[Status, bool]:  # pragma: no cover
        pass

    @abc.abstractmethod
    def _create_message(
        self, data: Dict[str, Any]
    ) -> Union[Awaitable, bool]:  # pragma: no cover
        pass

    def _create_status(self) -> Status:
        commands = []
        for command_name, handler in self._handlers.items():
            menu_command = handler.to_status_command()
            if menu_command:
                commands.append(menu_command)

        return Status(result=StatusResult(commands=commands))

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        if handler.use_as_default_handler:
            self._default_handler = handler
        else:
            self._handlers[handler.command] = handler


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
        cmd = message.command.cmd
        command = self._handlers.get(cmd)
        if command:
            await self._scheduler.spawn(command.func(message))
            return True
        else:
            if self._default_handler:
                print(self._default_handler)
                await self._scheduler.spawn(self._default_handler.func(message))
                return True
        return False

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        if not inspect.iscoroutinefunction(handler.func):
            raise BotXException("can not add not async handler to async dispatcher")

        super().add_handler(handler)


class SyncDispatcher(BaseDispatcher):
    _pool: ThreadPoolExecutor

    def __init__(self, workers: int):
        super().__init__()
        self._pool = ThreadPoolExecutor(max_workers=workers)

    def start(self) -> NoReturn:
        pass

    def shutdown(self) -> NoReturn:
        self._pool.shutdown()

    def parse_request(
        self, data: Dict[str, Any], request_type: Union[str, RequestTypeEnum]
    ) -> Union[Status, bool]:
        if request_type == RequestTypeEnum.status:
            return self._create_status()
        elif request_type == RequestTypeEnum.command:
            return self._create_message(data)
        else:
            raise BotXException(f"wrong request type {repr(request_type)}")

    def _create_message(self, data: Dict[str, Any]) -> bool:
        message = Message(**data)
        message.sync_id = SyncID(str(message.sync_id))

        cmd = message.command.cmd
        command = self._handlers.get(cmd)
        if command:
            self._pool.submit(command.func, message)
            return True
        else:
            if self._default_handler:
                self._pool.submit(self._default_handler.func, message=message)
                return True
        return False

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        if inspect.iscoroutinefunction(handler.func):
            raise BotXException("can not add async handler to sync dispatcher")

        super().add_handler(handler)
