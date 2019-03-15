import abc
from functools import partial
from typing import (
    Any,
    BinaryIO,
    Callable,
    Dict,
    List,
    NoReturn,
    Optional,
    TextIO,
    Union,
)
from uuid import UUID

from botx.types import (
    BubbleElement,
    KeyboardElement,
    ResponseRecipientsEnum,
    Status,
    SyncID,
)
from .dispatcher.basedispatcher import BaseDispatcher
from .dispatcher.commandhandler import CommandHandler


class BaseBot(abc.ABC):
    _dispatcher: BaseDispatcher
    _url_command: str = "https://{}/api/v2/botx/command/callback"
    _url_notification: str = "https://{}/api/v2/botx/notification/callback"
    _url_file: str = "https://{}/api/v1/botx/file/callback"

    def add_handler(self, handler: CommandHandler) -> NoReturn:
        self._dispatcher.add_handler(handler)

    def command(
        self,
        func: Optional[Callable] = None,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        body: Optional[str] = None,
        use_as_default_handler: bool = False,
        exclude_from_status: bool = False,
        system_command_handler: bool = False,
    ) -> Optional[Callable]:
        if func:
            name = name or "".join(
                func.__name__.lower().rsplit("command", 1)[0].rsplit("_", 1)
            )
            body = (
                (body if body.startswith("/") or system_command_handler else f"/{body}")
                if body
                else f"/{name}"
            )
            description = description or f"{name} command"

            self.add_handler(
                CommandHandler(
                    command=body,
                    func=func,
                    name=name.capitalize(),
                    description=description,
                    exclude_from_status=exclude_from_status,
                    use_as_default_handler=use_as_default_handler,
                    system_command_handler=system_command_handler,
                )
            )

            return func
        else:
            return partial(
                self.command,
                name=name,
                description=description,
                body=body,
                exclude_from_status=exclude_from_status,
                use_as_default_handler=use_as_default_handler,
                system_command_handler=system_command_handler,
            )

    @abc.abstractmethod
    def start(self) -> NoReturn:  # pragma: no cover
        pass

    @abc.abstractmethod
    def parse_status(self) -> Status:  # pragma: no cover
        pass

    @abc.abstractmethod
    def parse_command(self, data: Dict[str, Any]) -> bool:  # pragma: no cover
        pass

    @abc.abstractmethod
    def send_message(
        self,
        text: str,
        chat_id: Union[SyncID, UUID, List[UUID]],
        bot_id: UUID,
        host: str,
        *,
        recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all,
        bubble: Optional[List[List[BubbleElement]]] = None,
        keyboard: Optional[List[List[KeyboardElement]]] = None,
    ) -> str:  # pragma: no cover
        pass

    @abc.abstractmethod
    def _send_command_result(
        self,
        text: str,
        chat_id: SyncID,
        bot_id: UUID,
        host: str,
        recipients: Union[List[UUID], str],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ) -> str:  # pragma: no cover
        pass

    @abc.abstractmethod
    def _send_notification_result(
        self,
        text: str,
        group_chat_ids: List[UUID],
        bot_id: UUID,
        host: str,
        recipients: Union[List[UUID], str],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ) -> str:  # pragma: no cover
        pass

    @abc.abstractmethod
    def send_file(
        self,
        file: Union[TextIO, BinaryIO],
        chat_id: Union[SyncID, UUID],
        bot_id: UUID,
        host: str,
    ) -> str:  # pragma: no cover
        pass
