import abc
import inspect
import logging
from collections import OrderedDict
from threading import Lock
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    Tuple,
    Union,
)
from uuid import UUID

from botx import Message
from botx.core import BotXException
from botx.types import RequestTypeEnum, Status, StatusResult

from .command_handler import CommandHandler

if TYPE_CHECKING:
    from botx.bot.base_bot import BaseBot

LOGGER = logging.getLogger("botx")


class BaseDispatcher(abc.ABC):
    _handlers: Dict[str, CommandHandler]
    _lock: Lock
    _next_step_handlers: Dict[Tuple[str, UUID, UUID, Optional[UUID]], List[Callable]]
    _default_handler: Optional[CommandHandler] = None
    _bot: "BaseBot"

    def __init__(self, bot: "BaseBot"):
        self._handlers = OrderedDict()
        self._bot = bot
        self._next_step_handlers = {}
        self._lock = Lock()

    def start(self) -> NoReturn:
        """Start dispatcher-related things like aiojobs.Scheduler"""

    @abc.abstractmethod
    def shutdown(self) -> NoReturn:
        """Stop dispatcher-related things like thread or coroutine joining"""

    @abc.abstractmethod
    def parse_request(
        self, data: Dict[str, Any], request_type: Union[str, RequestTypeEnum]
    ) -> Union[Union[Status, bool], Awaitable[Union[Status, bool]]]:
        """Parse request and call status creation or executing handler for command"""

    def add_handler(self, handler: CommandHandler):
        if len(inspect.getfullargspec(handler.func).args) != 2:
            raise BotXException(
                "command handler for bot requires 2 arguments for message and for bot instance"
            )

        if handler.use_as_default_handler:
            LOGGER.debug("set default handler %r", handler.name)
            self._default_handler = handler
        else:
            LOGGER.debug("add new handler for %r", handler.command)
            self._handlers[handler.command] = handler

    @abc.abstractmethod
    def register_next_step_handler(self, message: Message, func):
        """Register next step handler"""

    @abc.abstractmethod
    def _create_message(self, data: Dict[str, Any]) -> Union[Awaitable, bool]:
        """Create new message for command handler and spawn worker for it"""

    def _create_status(self) -> Status:
        commands = []
        for _, handler in self._handlers.items():
            menu_command = handler.to_status_command()
            if menu_command:
                commands.append(menu_command)

        return Status(result=StatusResult(commands=commands))
