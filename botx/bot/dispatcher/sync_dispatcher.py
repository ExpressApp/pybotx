import inspect
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from functools import wraps
from typing import TYPE_CHECKING, Any, Dict, Union

from botx.core import BotXException
from botx.types import Message, RequestTypeEnum, Status

from .base_dispatcher import BaseDispatcher
from .command_handler import CommandHandler

if TYPE_CHECKING:
    from botx.bot.sync_bot import SyncBot

LOGGER = logging.getLogger("botx")


class SyncDispatcher(BaseDispatcher):
    _pool: ThreadPoolExecutor
    _bot: "SyncBot"

    def __init__(self, workers: int, bot: "SyncBot"):
        super().__init__(bot)
        self._pool = ThreadPoolExecutor(max_workers=workers)

    def shutdown(self):
        self._pool.shutdown()

    def parse_request(
        self, data: Dict[str, Any], request_type: Union[str, RequestTypeEnum]
    ) -> Union[Status, bool]:
        if request_type == RequestTypeEnum.status:
            return self._create_status()

        if request_type == RequestTypeEnum.command:
            return self._create_message(data)

        raise BotXException(f"wrong request type {repr(request_type)}")

    def add_handler(self, handler: CommandHandler):
        if inspect.iscoroutinefunction(handler.func):  # type: ignore
            raise BotXException("can not add async handler to sync dispatcher")

        def thread_logger_helper(func):
            @wraps(func)
            def wrapper(message, bot):
                try:
                    func(message, bot)
                except Exception as exc:
                    LOGGER.exception(exc)

            return wrapper

        handler.func = thread_logger_helper(handler.func)  # type: ignore

        super().add_handler(handler)

    def register_next_step_handler(self, message: Message, func):
        if inspect.iscoroutinefunction(func):
            raise BotXException("can not add async handler to sync dispatcher")

        def thread_logger_helper(f):
            @wraps(f)
            def wrapper(m, b):
                try:
                    func(m, b)
                except Exception as exc:
                    LOGGER.exception(exc)

            return wrapper

        key = (message.host, message.bot_id, message.group_chat_id, message.user_huid)
        with self._lock:
            if key in self._next_step_handlers:
                self._next_step_handlers[key].append(thread_logger_helper(func))
            else:
                self._next_step_handlers[key] = [thread_logger_helper(func)]

    def _create_message(self, data: Dict[str, Any]) -> bool:
        message = Message(**data)
        LOGGER.debug("message created: %r", message.json())

        try:
            key = (
                message.host,
                message.bot_id,
                message.group_chat_id,
                message.user_huid,
            )

            with self._lock:
                next_step_handler = self._next_step_handlers[
                    (
                        message.host,
                        message.bot_id,
                        message.group_chat_id,
                        message.user_huid,
                    )
                ].pop()

            LOGGER.debug("spawning next step handler for %r ", key)
            self._pool.submit(next_step_handler, message, self._bot)

            return True
        except (IndexError, KeyError):
            cmd = message.command.cmd
            command = self._handlers.get(cmd)
            func_to_spawn = None
            if command:
                LOGGER.debug("spawning command %r", cmd)
                func_to_spawn = command.func
            else:
                LOGGER.debug("no command found %r", cmd)
                if self._default_handler:
                    LOGGER.debug("spawning default handler")
                    func_to_spawn = self._default_handler.func

            if func_to_spawn:
                self._pool.submit(func_to_spawn, message, self._bot)

                return True

            LOGGER.debug("default handler was not set")
            return False
