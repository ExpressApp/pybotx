import asyncio
from collections import OrderedDict

import abc
import aiojobs
import inspect
import asgiref.sync
import uuid
from concurrent.futures.process import ProcessPoolExecutor
from enum import Enum
from typing import Dict, Any, Union, NoReturn, Optional, Callable, Awaitable

from botx.bot import Bot
from botx.exception import BotXException
from botx.types import Message, Status, StatusResult
from .commandhandler import CommandHandler


class RequestTypeEnum(str, Enum):
    status: str = "status"
    command: str = "command"


class Dispatcher(abc.ABC):
    _bot: Bot
    _handlers: Dict[str, CommandHandler]
    _default_handler: Optional[CommandHandler] = None

    def __init__(self, bot: Bot):
        self._bot = bot
        self._handlers = OrderedDict()

    @abc.abstractmethod
    def shutdown(self) -> NoReturn:
        pass

    @abc.abstractmethod
    def parse_request(
        self, data: Dict[str, Any], request_type: Union[str, RequestTypeEnum]
    ) -> Union[Status, bool]:
        pass

    @abc.abstractmethod
    def _create_message(self, data: Dict[str, Any]) -> Union[Awaitable, bool]:
        pass

    def _check_bot_id(self, data: Dict[str, Any]) -> NoReturn:
        if "bot_id" not in data:
            raise BotXException("missing bot_id field in data")
        if not uuid.UUID(data["bot_id"]) != self._bot.bot_id:
            raise BotXException("mismatched_bot_id from data")

    def _create_status(self, data: Dict[str, Any]) -> Status:
        self._check_bot_id(data)

        commands = []
        for command_name, handler in self._handlers.items():
            if not handler.exclude_from_status:
                commands.append(handler.to_status_command())

        return Status(result=StatusResult(commands=commands))

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        if handler.use_as_default_handler:
            self._default_handler = handler
        else:
            self._handlers[handler.command] = handler


class AsyncDispatcher(Dispatcher):
    _scheduler = aiojobs.Scheduler

    def __init__(self, bot: Bot):
        super().__init__(bot)
        self._scheduler: aiojobs.Scheduler = asgiref.sync.async_to_sync(
            aiojobs.create_scheduler
        )()

    async def shutdown(self) -> NoReturn:
        await self._scheduler.close()

    async def parse_request(
        self, data: Dict[str, Any], request_type: Union[str, RequestTypeEnum]
    ) -> Union[Status, bool]:
        if request_type == RequestTypeEnum.status:
            return self._create_status(data)
        elif request_type == RequestTypeEnum.command:
            return await self._create_message(data)

    async def _create_message(self, data: Dict[str, Any]) -> bool:
        self._check_bot_id(data)

        message = Message(**data)
        cmd = message.command.cmd
        command = self._handlers.get(cmd)
        if command:
            await self._scheduler.spawn(command.func(message))
            return True
        else:
            if self._default_handler:
                await self._scheduler.spawn(command.func(message))
                return True
        return False

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        if not inspect.isawaitable(handler.func):
            raise BotXException("can not add not async handler to async dispatcher")

        super().add_handler(handler)


class SyncDispatcher(Dispatcher):
    _pool: ProcessPoolExecutor

    def __init__(self, bot: Bot, workers: int):
        super().__init__(bot)
        self._pool = ProcessPoolExecutor(max_workers=workers)

    def shutdown(self) -> NoReturn:
        self._pool.shutdown()

    def parse_request(
        self, data: Dict[str, Any], request_type: Union[str, RequestTypeEnum]
    ) -> Union[Status, bool]:
        if request_type == RequestTypeEnum.status:
            return self._create_status(data)
        elif request_type == RequestTypeEnum.command:
            return self._create_message(data)
        else:
            raise BotXException(f"wrong request type {repr(request_type)}")

    def _create_message(self, data: Dict[str, Any]) -> bool:
        self._check_bot_id(data)

        message = Message(**data)
        cmd = message.command.cmd
        command = self._handlers.get(cmd)
        if command:
            self._pool.submit(command.func, message=message)
            return True
        else:
            if self._default_handler:
                self._pool.submit(command.func, message=message)
                return True
        return False

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        if inspect.isawaitable(handler.func):
            raise BotXException("can not add async handler to sync dispatcher")

        super().add_handler(handler)
