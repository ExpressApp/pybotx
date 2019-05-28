import abc
import logging
from typing import Any, Awaitable, BinaryIO, Dict, List, Optional, TextIO, Tuple, Union
from uuid import UUID

from botx.core import BotXAPI
from botx.types import (
    CTS,
    BotCredentials,
    BubbleElement,
    File,
    KeyboardElement,
    Mention,
    Message,
    ResponseRecipientsEnum,
    Status,
    SyncID,
)

from .dispatcher.base_dispatcher import BaseDispatcher
from .dispatcher.command_handler import CommandHandler
from .router import CommandRouter

LOGGER = logging.getLogger("botx")


class BaseBot(abc.ABC, CommandRouter):
    _dispatcher: BaseDispatcher
    _credentials: BotCredentials
    _disable_credentials: bool
    _url_token: str = BotXAPI.V2.token.url
    _url_command: str = BotXAPI.V3.command.url
    _url_notification: str = BotXAPI.V3.notification.url
    _url_file: str = BotXAPI.V1.file.url

    def __init__(
        self,
        *,
        credentials: Optional[BotCredentials] = None,
        disable_credentials: bool = False,
    ):
        super().__init__()

        self._credentials = credentials if credentials else BotCredentials()

        if disable_credentials:
            LOGGER.warning("token obtaining disabled")
            self._url_command = BotXAPI.V2.command.url
            self._url_notification = BotXAPI.V2.notification.url

        self._disable_credentials = disable_credentials

    @property
    def credentials(self) -> BotCredentials:
        return self._credentials

    def add_bot_credentials(self, credentials: BotCredentials):
        LOGGER.debug("add new credentials for bot %r", credentials.json())
        self._credentials.known_cts = [
            cts
            for host, cts in {
                cts.host: cts
                for cts in self._credentials.known_cts + credentials.known_cts
            }.items()
        ]

    def add_cts(self, cts: CTS):
        LOGGER.debug("register new CTS %r for bot", cts.host)
        self._credentials.known_cts.append(cts)

    def add_handler(self, handler: CommandHandler):
        self._dispatcher.add_handler(handler)

    def add_commands(self, router: CommandRouter):
        for _, handler in router.handlers.items():
            self.add_handler(handler)

    def get_cts_by_host(self, host: str) -> Optional[CTS]:
        return {cts.host: cts for cts in self.credentials.known_cts}.get(host)

    def start(self):
        """Run some outer dependencies that can not be started in init"""

    @abc.abstractmethod
    def stop(self):
        """Stop special objects and dispatcher for bot"""

    @abc.abstractmethod
    def parse_status(self) -> Union[Status, Awaitable[Status]]:
        """Create status object for bot"""

    @abc.abstractmethod
    def parse_command(self, data: Dict[str, Any]) -> Union[bool, Awaitable[bool]]:
        """Execute command from request"""

    @abc.abstractmethod
    def send_message(
        self,
        text: str,
        chat_id: Union[SyncID, UUID, List[UUID]],
        bot_id: UUID,
        host: str,
        *,
        file: Optional[Union[TextIO, BinaryIO]] = None,
        recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all,
        mentions: Optional[List[Mention]] = None,
        bubble: Optional[List[List[BubbleElement]]] = None,
        keyboard: Optional[List[List[KeyboardElement]]] = None,
    ) -> Union[Tuple[str, int], Awaitable[Tuple[str, int]]]:
        """Create answer for notification or for command and send it to BotX API"""

    @abc.abstractmethod
    def answer_message(
        self,
        text: str,
        message: Message,
        *,
        file: Optional[Union[TextIO, BinaryIO]] = None,
        recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all,
        mentions: Optional[List[Mention]] = None,
        bubble: Optional[List[List[BubbleElement]]] = None,
        keyboard: Optional[List[List[KeyboardElement]]] = None,
    ) -> Union[Tuple[str, int], Awaitable[Tuple[str, int]]]:
        """Send message with credentials from incoming message"""

    @abc.abstractmethod
    def send_file(
        self,
        file: Union[TextIO, BinaryIO],
        chat_id: Union[SyncID, UUID],
        bot_id: UUID,
        host: str,
    ) -> Union[Tuple[str, int], Awaitable[Tuple[str, int]]]:
        """Send separate file to BotX API"""

    def register_next_step_handler(self, message: Message, func):
        if message.user_huid:
            self._dispatcher.register_next_step_handler(message, func)

    def _set_cts_credentials(self, new_cts: CTS):
        i = [
            i
            for i, cts in enumerate(self._credentials.known_cts)
            if cts.host == new_cts.host
        ][0]
        self._credentials.known_cts[i] = new_cts

    def _get_token_from_cts(self, host: str) -> Optional[str]:
        cts = self.get_cts_by_host(host)
        if not cts or not cts.credentials:
            LOGGER.debug("no credentials for %r found", host)
            return None

        return cts.credentials.token

    @abc.abstractmethod
    def _obtain_token(
        self, host: str, bot_id: UUID
    ) -> Union[Tuple[str, int], Awaitable[Tuple[str, int]]]:
        """Obtain token from BotX for making requests"""

    @abc.abstractmethod
    def _send_command_result(
        self,
        text: str,
        chat_id: SyncID,
        bot_id: UUID,
        host: str,
        file: Optional[File],
        recipients: Union[List[UUID], str],
        mentions: List[Mention],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ) -> Union[Tuple[str, int], Awaitable[Tuple[str, int]]]:
        """Send command result answer"""

    @abc.abstractmethod
    def _send_notification_result(
        self,
        text: str,
        group_chat_ids: List[UUID],
        bot_id: UUID,
        host: str,
        file: Optional[File],
        recipients: Union[List[UUID], str],
        mentions: List[Mention],
        bubble: List[List[BubbleElement]],
        keyboard: List[List[KeyboardElement]],
    ) -> Union[Tuple[str, int], Awaitable[Tuple[str, int]]]:
        """Send notification result answer"""
