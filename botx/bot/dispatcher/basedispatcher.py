from collections import OrderedDict

import abc
from typing import Any, Awaitable, Dict, NoReturn, Optional, Union

from botx.types import RequestTypeEnum, Status, StatusResult
from .commandhandler import CommandHandler


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
