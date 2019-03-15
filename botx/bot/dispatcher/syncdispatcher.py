import inspect
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Any, Dict, NoReturn, Union

from botx.core import BotXException
from botx.types import Message, RequestTypeEnum, Status, SyncID
from .basedispatcher import BaseDispatcher
from .commandhandler import CommandHandler


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
