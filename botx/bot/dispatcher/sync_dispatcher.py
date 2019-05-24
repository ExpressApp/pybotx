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
    from botx.bot.sync_bot import SyncBot  # pylint: disable=cyclic-import

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

    def _create_message(self, data: Dict[str, Any]) -> bool:
        message = Message(**data)
        LOGGER.debug("message created: %r", message.json())

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

    def add_handler(self, handler: CommandHandler):
        if inspect.iscoroutinefunction(handler.func):
            raise BotXException("can not add async handler to sync dispatcher")

        def thread_logger_helper(func):
            @wraps(func)
            def wrapper(message, bot):
                try:
                    func(message, bot)
                except Exception as exc:  # pylint: disable=broad-except
                    LOGGER.exception(exc)

            return wrapper

        handler.func = thread_logger_helper(handler.func)  # type: ignore

        super().add_handler(handler)
