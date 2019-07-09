import abc
import asyncio
from collections import OrderedDict
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Lock
from typing import Any, Awaitable, Dict, List, Optional, Pattern, Tuple
from uuid import UUID

import aiojobs
import asgiref.sync
from loguru import logger

from .core import BotXException
from .helpers import create_message, logger_wrapper
from .models import CommandCallback, CommandHandler, Message, Status, StatusResult


class BaseDispatcher(abc.ABC):
    _handlers: Dict[Pattern, CommandHandler]
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
        logger_ctx = logger.bind(handler=handler.dict())

        if handler.use_as_default_handler:
            logger_ctx.debug("registered default handler")

            self._default_handler = handler
        else:
            logger_ctx.debug(f"registered handler for {handler.command}")

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

    def _get_callback_for_message(self, message: Message) -> CommandCallback:
        logger_ctx = logger.bind(message=message.dict())

        try:
            callback = self._get_next_step_handler_from_message(message)
            logger_ctx.bind(callback=callback.dict()).debug(
                "found registered next step handler for message"
            )
        except (IndexError, KeyError):
            callback = self._get_command_handler_from_message(message).callback
            logger_ctx.bind(command=message.command.command).debug(
                "found handler for command"
            )

        return callback

    def _get_next_step_handler_from_message(self, message: Message) -> CommandCallback:
        with self._lock:
            return self._next_step_handlers[
                (message.host, message.bot_id, message.group_chat_id, message.user_huid)
            ].pop()

    def _get_command_handler_from_message(self, message: Message) -> CommandHandler:
        body = message.command.body
        cmd = message.command.command

        handler = None
        for cmd_pattern in self._handlers:
            if cmd_pattern.fullmatch(body):
                handler = self._handlers[cmd_pattern]
                break
            elif cmd_pattern.fullmatch(cmd):
                handler = self._handlers[cmd_pattern]
                break

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
        logger.bind(message=message.dict()).debug("parsed message successful")

        callback = self._get_callback_for_message(message)

        self._pool.submit(callback.callback, message, *callback.args, **callback.kwargs)

    def add_handler(self, handler: CommandHandler) -> None:
        if asyncio.iscoroutinefunction(handler.callback.callback):
            logger.bind(handler=handler.dict()).debug(
                "transforming handler callback coroutine to function"
            )
            handler.callback.callback = asgiref.sync.async_to_sync(  # type: ignore
                handler.callback.callback
            )

        func = handler.callback.callback

        # mypy can not recognize assigment to functions; see #2427
        handler.callback.callback = logger_wrapper(func=func)  # type: ignore
        super().add_handler(handler)

    def register_next_step_handler(
        self, message: Message, callback: CommandCallback
    ) -> None:
        if asyncio.iscoroutinefunction(callback.callback):
            logger_ctx = logger.bind(callback=callback.dict())
            logger_ctx.warning("transforming function in runtime is not cheap")
            logger_ctx.debug("transforming handler callback coroutine to function")

            callback.callback = asgiref.sync.async_to_sync(  # type: ignore
                callback.callback
            )

        func = callback.callback

        # mypy can not recognize assigment to functions; see #2427
        callback.callback = logger_wrapper(func=func)  # type: ignore
        self._add_next_step_handler(message, callback)


class AsyncDispatcher(BaseDispatcher):
    _scheduler: aiojobs.Scheduler
    _tasks_limit: int

    def __init__(self, tasks_limit: int) -> None:
        super().__init__()
        self._tasks_limit = tasks_limit

    async def start(self) -> None:
        self._scheduler = await aiojobs.create_scheduler(
            limit=self._tasks_limit, pending_limit=0
        )

    async def shutdown(self) -> None:
        await self._scheduler.close()

    async def execute_command(self, data: Dict[str, Any]) -> None:
        message = create_message(data)
        logger.bind(message=message.dict()).debug("parsed message successful")

        callback = self._get_callback_for_message(message)
        await self._scheduler.spawn(
            callback.callback(message, *callback.args, **callback.kwargs)
        )

    def add_handler(self, handler: CommandHandler) -> None:
        if not asyncio.iscoroutinefunction(handler.callback.callback):
            logger.bind(handler=handler.dict()).debug(
                "transforming handler callback to coroutine"
            )
            handler.callback.callback = asgiref.sync.sync_to_async(  # type: ignore
                handler.callback.callback
            )

        super().add_handler(handler)

    def register_next_step_handler(
        self, message: Message, callback: CommandCallback
    ) -> None:
        if not asyncio.iscoroutinefunction(callback.callback):
            logger_ctx = logger.bind(callback=callback.dict())
            logger_ctx.warning("transforming function in runtime is not cheap")
            logger_ctx.debug("transforming handler callback to coroutine")

            callback.callback = asgiref.sync.async_to_sync(  # type: ignore
                callback.callback
            )

        self._add_next_step_handler(message, callback)
