import inspect
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Any, Dict, NoReturn, Union

from botx.core import BotXException
from botx.types import Message, RequestTypeEnum, Status

from .basedispatcher import BaseDispatcher
from .commandhandler import CommandHandler

LOGGER = logging.getLogger("botx")


class SyncDispatcher(BaseDispatcher):
    _pool: ThreadPoolExecutor
    _bot: "SyncBot"

    def __init__(self, workers: int, bot: "SyncBot"):
        super().__init__(bot)
        self._pool = ThreadPoolExecutor(max_workers=workers)

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
        LOGGER.debug(f"message created: {message.json() !r}")

        cmd = message.command.cmd
        command = self._handlers.get(cmd)
        if command:
            LOGGER.debug(f"spawning command {cmd !r}")
            self._pool.submit(command.func, message=message, bot=self._bot)
            return True
        else:
            LOGGER.debug(f"no command {cmd !r} found")
            if self._default_handler:
                LOGGER.debug("spawning default handler")
                self._pool.submit(
                    self._default_handler.func, message=message, bot=self._bot
                )
                return True

        LOGGER.debug("default handler was not set")
        return False

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        if inspect.iscoroutinefunction(handler.func):
            raise BotXException("can not add async handler to sync dispatcher")

        super().add_handler(handler)
