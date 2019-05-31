import abc
import asyncio
import logging
from collections import OrderedDict
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Lock
from typing import Any, Awaitable, Dict, List, Optional, Tuple
from uuid import UUID

import aiojobs

from .core import BotXException
from .helpers import create_message, thread_logger_wrapper
from .models import CommandCallback, CommandHandler, Message, Status, StatusResult

BOTX_LOGGER = logging.getLogger("botx")


class BaseDispatcher(abc.ABC):
    _handlers: Dict[str, CommandHandler]
    _lock: Lock
    _next_step_handlers: Dict[
        Tuple[str, UUID, UUID, Optional[UUID]], List[CommandCallback]
    ]
    _default_handler: Optional[CommandHandler] = None

    def __init__(self) -> None:
        self._handlers = OrderedDict()
        self._next_step_handlers = {}
        self._lock = Lock()

    def start(self) -> Optional[Awaitable[None]]:
        """Start dispatcher-related things like aiojobs.Scheduler"""

    def shutdown(self) -> Optional[Awaitable[None]]:
        """Stop dispatcher-related things like thread or coroutine joining"""

    @property
    def status(self) -> Status:
        commands = []
        for _, handler in self._handlers.items():
            menu_command = handler.to_status_command()
            if menu_command:
                commands.append(menu_command)

        return Status(result=StatusResult(commands=commands))

    @abc.abstractmethod
    def execute_command(self, data: Dict[str, Any]) -> Optional[Awaitable[None]]:
        """Parse request and call status creation or executing handler for handler"""

    def add_handler(self, handler: CommandHandler) -> None:
        if handler.use_as_default_handler:
            BOTX_LOGGER.debug("registered default handler")

            self._default_handler = handler
        else:
            BOTX_LOGGER.debug(f"registered handler for {handler.command}")

            self._handlers[handler.command] = handler

    @abc.abstractmethod
    def register_next_step_handler(
        self, message: Message, callback: CommandCallback
    ) -> None:
        """Register next step handler"""

    def _add_next_step_handler(
        self, message: Message, callback: CommandCallback
    ) -> None:
        key = (message.host, message.bot_id, message.group_chat_id, message.user_huid)
        with self._lock:
            if key in self._next_step_handlers:
                self._next_step_handlers[key].append(callback)
            else:
                self._next_step_handlers[key] = [callback]

    def _get_next_step_handler_from_message(self, message: Message) -> CommandCallback:
        with self._lock:
            return self._next_step_handlers[
                (message.host, message.bot_id, message.group_chat_id, message.user_huid)
            ].pop()

    def _get_command_handler_from_message(self, message: Message) -> CommandHandler:
        cmd = message.command.command

        handler = self._handlers.get(cmd)

        if handler:
            return handler

        if self._default_handler:
            return self._default_handler

        raise BotXException(
            "unhandled command with missing handler", data={"handler": message.body}
        )


class SyncDispatcher(BaseDispatcher):
    _pool: ThreadPoolExecutor

    def __init__(self, workers: int) -> None:
        super().__init__()

        self._pool = ThreadPoolExecutor(max_workers=workers)

    def shutdown(self) -> None:
        self._pool.shutdown()

    def execute_command(self, data: Dict[str, Any]) -> None:
        message = create_message(data)

        try:
            callback = self._get_next_step_handler_from_message(message)
            self._pool.submit(
                callback.callback, message, *callback.args, **callback.kwargs
            )
        except (IndexError, KeyError):
            handler = self._get_command_handler_from_message(message)
            self._pool.submit(
                handler.callback.callback,
                message,
                *handler.callback.args,
                **handler.callback.kwargs,
            )

    def add_handler(self, handler: CommandHandler) -> None:
        if asyncio.iscoroutinefunction(handler.callback.callback):
            raise BotXException("can not add async handler to sync dispatcher")

        func = handler.callback.callback

        # mypy can not recognize assigment to functions; see #2427
        handler.callback.callback = thread_logger_wrapper(func=func)  # type: ignore
        super().add_handler(handler)

    def register_next_step_handler(
        self, message: Message, callback: CommandCallback
    ) -> None:
        if asyncio.iscoroutinefunction(callback.callback):
            raise BotXException("can not add async handler to sync dispatcher")

        func = callback.callback

        # mypy can not recognize assigment to functions; see #2427
        callback.callback = thread_logger_wrapper(func=func)  # type: ignore
        self._add_next_step_handler(message, callback)


class AsyncDispatcher(BaseDispatcher):
    _scheduler: aiojobs.Scheduler

    async def start(self) -> None:
        self._scheduler = await aiojobs.create_scheduler()

    async def shutdown(self) -> None:
        await self._scheduler.close()

    async def execute_command(self, data: Dict[str, Any]) -> None:
        message = create_message(data)

        try:
            callback = self._get_next_step_handler_from_message(message)
            await self._scheduler.spawn(
                callback.callback(message, *callback.args, **callback.kwargs)
            )
        except KeyError:
            handler = self._get_command_handler_from_message(message)
            await self._scheduler.spawn(
                handler.callback.callback(
                    message, *handler.callback.args, **handler.callback.kwargs
                )
            )

    def add_handler(self, handler: CommandHandler) -> None:
        if not asyncio.iscoroutinefunction(handler.callback.callback):
            raise BotXException("can not add not async handler to async dispatcher")

        super().add_handler(handler)

    def register_next_step_handler(
        self, message: Message, callback: CommandCallback
    ) -> None:
        if not asyncio.iscoroutinefunction(callback.callback):
            raise BotXException("can not add not async handler to async dispatcher")

        self._add_next_step_handler(message, callback)
