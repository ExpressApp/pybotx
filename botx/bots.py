import abc
import logging
import multiprocessing
from typing import (
    Any,
    Awaitable,
    BinaryIO,
    Callable,
    Dict,
    List,
    Optional,
    TextIO,
    Union,
)
from uuid import UUID

import aiohttp
import requests

from .collector import HandlersCollector
from .core import TEXT_MAX_LENGTH, BotXAPI, BotXException
from .dispatchers import AsyncDispatcher, BaseDispatcher, SyncDispatcher
from .helpers import (
    get_data_for_api_error_async,
    get_data_for_api_error_sync,
    get_headers,
)
from .models import (
    CTS,
    BotCredentials,
    BubbleElement,
    CommandCallback,
    CommandHandler,
    CTSCredentials,
    File,
    KeyboardElement,
    Mention,
    Message,
    NotificationOpts,
    ReplyMessage,
    ResponseCommand,
    ResponseFile,
    ResponseNotification,
    ResponseRecipientsEnum,
    ResponseResult,
    Status,
    SyncID,
)

BOTX_LOGGER = logging.getLogger("botx")
CPU_COUNT = multiprocessing.cpu_count()


class BaseBot(abc.ABC, HandlersCollector):
    _dispatcher: BaseDispatcher
    _credentials: BotCredentials
    _disable_credentials: bool
    _token_url: str = BotXAPI.V2.token.url
    _command_url: str = BotXAPI.V3.command.url
    _notification_url: str = BotXAPI.V3.notification.url
    _file_url: str = BotXAPI.V1.file.url

    def __init__(
        self,
        *,
        credentials: Optional[BotCredentials] = None,
        disable_credentials: bool = False,
    ) -> None:
        super().__init__()

        self._credentials = credentials if credentials else BotCredentials()

        if disable_credentials:
            BOTX_LOGGER.debug("tokens obtaining disabled")

            self._command_url = BotXAPI.V2.command.url
            self._notification_url = BotXAPI.V2.notification.url

        self._disable_credentials = disable_credentials

    @property
    def credentials(self) -> BotCredentials:
        return self._credentials

    def add_credentials(self, credentials: BotCredentials) -> None:
        self._credentials.known_cts = [
            cts
            for host, cts in {
                cts.host: cts
                for cts in self._credentials.known_cts + credentials.known_cts
            }.items()
        ]

    def add_cts(self, cts: CTS) -> None:
        self._credentials.known_cts.append(cts)

    def add_handler(self, handler: CommandHandler, force_replace: bool = False) -> None:
        handler.callback.args = (self,) + handler.callback.args
        super().add_handler(handler, force_replace)
        self._dispatcher.add_handler(handler)

    def get_cts_by_host(self, host: str) -> Optional[CTS]:
        return {cts.host: cts for cts in self.credentials.known_cts}.get(host)

    def get_token_from_cts(self, host: str) -> str:
        cts = self.get_cts_by_host(host)
        if cts and cts.credentials:
            return cts.credentials.token

        raise BotXException(f"no token found for cts with {host} host")

    def start(self) -> Optional[Awaitable[None]]:
        """Run some outer dependencies that can not be started in init"""

    def stop(self) -> Optional[Awaitable[None]]:
        """Stop special objects and dispatcher for bot"""

    @property
    def status(self) -> Status:
        return self._dispatcher.status

    @abc.abstractmethod
    def execute_command(self, data: Dict[str, Any]) -> Optional[Awaitable[None]]:
        """Execute handler from request"""

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
        opts: Optional[NotificationOpts] = None,
    ) -> Optional[Awaitable[None]]:
        """Create answer for notification or for handler and send it to BotX API"""

    @abc.abstractmethod
    def reply(self, message: ReplyMessage) -> Optional[Awaitable[None]]:
        """Reply for handler in shorter form using ReplyMessage"""

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
        opts: Optional[NotificationOpts] = None,
    ) -> Optional[Awaitable[None]]:
        """Send message with credentials from incoming message"""

    @abc.abstractmethod
    def send_file(
        self,
        file: Union[TextIO, BinaryIO],
        chat_id: Union[SyncID, UUID],
        bot_id: UUID,
        host: str,
    ) -> Optional[Awaitable[None]]:
        """Send separate file to BotX API"""

    def register_next_step_handler(
        self, message: Message, callback: Callable, *args: Any, **kwargs: Any
    ) -> None:
        if message.user_huid:
            self._dispatcher.register_next_step_handler(
                message,
                CommandCallback(callback=callback, args=(self, *args), kwargs=kwargs),
            )
        else:
            raise BotXException(
                "next step handlers registration is available "
                "only for messages from real users"
            )

    @abc.abstractmethod
    def _obtain_token(self, host: str, bot_id: UUID) -> Optional[Awaitable[None]]:
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
        opts: NotificationOpts,
    ) -> Optional[Awaitable[None]]:
        """Send handler result answer"""

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
        opts: NotificationOpts,
    ) -> Optional[Awaitable[None]]:
        """Send notification result answer"""


class SyncBot(BaseBot):
    _dispatcher: SyncDispatcher
    _session: requests.Session

    def __init__(
        self,
        *,
        workers: int = CPU_COUNT,
        credentials: Optional[BotCredentials] = None,
        disable_credentials: bool = False,
    ) -> None:
        super().__init__(
            credentials=credentials, disable_credentials=disable_credentials
        )

        self._dispatcher = SyncDispatcher(workers=workers)
        self._session = requests.Session()

    def start(self) -> None:
        self._dispatcher.start()

    def stop(self) -> None:
        self._dispatcher.shutdown()
        self._session.close()

    def execute_command(self, data: Dict[str, Any]) -> None:
        self._dispatcher.execute_command(data)

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
        opts: Optional[NotificationOpts] = None,
    ) -> None:
        bubble = bubble or []
        keyboard = keyboard or []
        mentions = mentions or []
        opts = opts or NotificationOpts()

        if len(text) > TEXT_MAX_LENGTH:
            raise BotXException(
                f"message text must be shorter {TEXT_MAX_LENGTH} symbols"
            )

        self._obtain_token(host, bot_id)

        response_file = File.from_file(file) if file else None

        if isinstance(chat_id, SyncID):
            return self._send_command_result(
                text=text,
                chat_id=chat_id,
                bot_id=bot_id,
                host=host,
                file=response_file,
                recipients=recipients,
                mentions=mentions,
                bubble=bubble,
                keyboard=keyboard,
                opts=opts,
            )
        else:
            group_chat_ids = []
            if isinstance(chat_id, UUID):
                group_chat_ids.append(chat_id)
            else:
                group_chat_ids = chat_id

            return self._send_notification_result(
                text=text,
                group_chat_ids=group_chat_ids,
                bot_id=bot_id,
                host=host,
                file=response_file,
                recipients=recipients,
                mentions=mentions,
                bubble=bubble,
                keyboard=keyboard,
                opts=opts,
            )

    def reply(self, message: ReplyMessage) -> None:
        self.send_message(
            message.text,
            message.chat_id,
            message.bot_id,
            message.host,
            file=message.file.file if message.file else None,
            recipients=message.recipients,
            mentions=message.mentions,
            bubble=message.bubble,
            keyboard=message.keyboard,
            opts=message.opts,
        )

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
        opts: Optional[NotificationOpts] = None,
    ) -> None:
        self.send_message(
            text,
            message.sync_id,
            message.bot_id,
            message.host,
            file=file,
            recipients=recipients,
            mentions=mentions,
            bubble=bubble,
            keyboard=keyboard,
            opts=opts,
        )

    def send_file(
        self,
        file: Union[TextIO, BinaryIO],
        chat_id: Union[SyncID, UUID],
        bot_id: UUID,
        host: str,
    ) -> None:
        self._obtain_token(host, bot_id)

        files = {"file": file}
        response = ResponseFile(bot_id=bot_id, sync_id=chat_id).dict()

        BOTX_LOGGER.debug("sending file: %s", {"file_response": response})

        resp = self._session.post(
            self._file_url.format(host=host), data=response, files=files
        )
        if resp.status_code >= 400:
            raise BotXException(
                "unable to send file to botx",
                data=get_data_for_api_error_sync(
                    host=host, bot_id=bot_id, response=resp, chat_ids=chat_id
                ),
            )

    def _obtain_token(self, host: str, bot_id: UUID) -> None:
        if self._disable_credentials:
            return

        cts = self.get_cts_by_host(host)
        if not cts:
            raise BotXException(f"unregistered cts with host {repr(host)}")

        if cts.credentials and cts.credentials.token:
            return

        signature = cts.calculate_signature(bot_id)

        BOTX_LOGGER.debug("calculated signature for %s: %s", cts.host, signature)

        resp = self._session.get(
            self._token_url.format(host=host, bot_id=bot_id),
            params={"signature": signature},
        )
        if resp.status_code >= 400:
            raise BotXException(
                "unable to obtain token from botx",
                data=get_data_for_api_error_sync(
                    host=host, bot_id=bot_id, response=resp
                ),
            )

        token = resp.json().get("result")

        cts.credentials = CTSCredentials(bot_id=bot_id, token=token)

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
        opts: NotificationOpts,
    ) -> None:
        command_resp = ResponseCommand(
            bot_id=bot_id,
            sync_id=chat_id,
            command_result=ResponseResult(
                body=text, bubble=bubble, keyboard=keyboard, mentions=mentions
            ),
            recipients=recipients,
            file=file,
            opts=opts,
        )
        headers = (
            get_headers(self.get_token_from_cts(host))
            if not self._disable_credentials
            else {}
        )

        BOTX_LOGGER.debug(
            "sending command response: %s",
            {"command_response": command_resp.json(), "headers": headers},
        )

        resp = self._session.post(
            self._command_url.format(host=host),
            json=command_resp.dict(),
            headers=headers,
        )
        if resp.status_code >= 400:
            raise BotXException(
                "unable to send handler result",
                data=get_data_for_api_error_sync(
                    host=host, bot_id=bot_id, response=resp, chat_ids=chat_id
                ),
            )

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
        opts: NotificationOpts,
    ) -> None:
        notification_resp = ResponseNotification(
            bot_id=bot_id,
            group_chat_ids=group_chat_ids,
            notification=ResponseResult(
                body=text, bubble=bubble, keyboard=keyboard, mentions=mentions
            ),
            recipients=recipients,
            file=file,
            opts=opts,
        )
        headers = (
            get_headers(self.get_token_from_cts(host))
            if not self._disable_credentials
            else {}
        )

        BOTX_LOGGER.debug(
            "sending notification response: %s",
            {"notification_response": notification_resp.json(), "headers": headers},
        )

        resp = self._session.post(
            self._notification_url.format(host=host),
            json=notification_resp.dict(),
            headers=headers,
        )
        if resp.status_code >= 400:
            raise BotXException(
                "unable to send notification result",
                data=get_data_for_api_error_sync(
                    host=host, bot_id=bot_id, response=resp, chat_ids=group_chat_ids
                ),
            )


class AsyncBot(BaseBot):
    _session: aiohttp.ClientSession
    _dispatcher: AsyncDispatcher

    def __init__(
        self,
        *,
        credentials: Optional[BotCredentials] = None,
        disable_credentials: bool = False,
    ) -> None:
        super().__init__(
            credentials=credentials, disable_credentials=disable_credentials
        )

        self._dispatcher = AsyncDispatcher()

    async def start(self) -> None:
        await self._dispatcher.start()
        self._session = aiohttp.ClientSession()

    async def stop(self) -> None:
        await self._dispatcher.shutdown()
        await self._session.close()

    async def execute_command(self, data: Dict[str, Any]) -> None:
        await self._dispatcher.execute_command(data)

    async def send_message(
        self,
        text: str,
        chat_id: Union[SyncID, UUID, List[UUID]],
        bot_id: UUID,
        host: str,
        *,
        file: Optional[Union[BinaryIO, TextIO]] = None,
        recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all,
        mentions: Optional[List[Mention]] = None,
        bubble: Optional[List[List[BubbleElement]]] = None,
        keyboard: Optional[List[List[KeyboardElement]]] = None,
        opts: Optional[NotificationOpts] = None,
    ) -> None:
        bubble = bubble or []
        keyboard = keyboard or []
        mentions = mentions or []
        opts = opts or NotificationOpts()

        if len(text) > TEXT_MAX_LENGTH:
            raise BotXException(
                f"message text must be shorter {TEXT_MAX_LENGTH} symbols"
            )

        await self._obtain_token(host, bot_id)

        response_file = File.from_file(file) if file else None

        if isinstance(chat_id, SyncID):
            return await self._send_command_result(
                text=text,
                chat_id=chat_id,
                bot_id=bot_id,
                host=host,
                file=response_file,
                recipients=recipients,
                mentions=mentions,
                bubble=bubble,
                keyboard=keyboard,
                opts=opts,
            )
        else:
            group_chat_ids = []
            if isinstance(chat_id, UUID):
                group_chat_ids.append(chat_id)
            else:
                group_chat_ids = chat_id

            return await self._send_notification_result(
                text=text,
                group_chat_ids=group_chat_ids,
                bot_id=bot_id,
                host=host,
                file=response_file,
                recipients=recipients,
                mentions=mentions,
                bubble=bubble,
                keyboard=keyboard,
                opts=opts,
            )

    async def reply(self, message: ReplyMessage) -> None:
        await self.send_message(
            message.text,
            message.chat_id,
            message.bot_id,
            message.host,
            file=message.file.file if message.file else None,
            recipients=message.recipients,
            mentions=message.mentions,
            bubble=message.bubble,
            keyboard=message.keyboard,
            opts=message.opts,
        )

    async def answer_message(
        self,
        text: str,
        message: Message,
        *,
        file: Optional[Union[TextIO, BinaryIO]] = None,
        recipients: Union[List[UUID], str] = ResponseRecipientsEnum.all,
        mentions: Optional[List[Mention]] = None,
        bubble: Optional[List[List[BubbleElement]]] = None,
        keyboard: Optional[List[List[KeyboardElement]]] = None,
        opts: Optional[NotificationOpts] = None,
    ) -> None:
        await self.send_message(
            text,
            message.sync_id,
            message.bot_id,
            message.host,
            file=file,
            recipients=recipients,
            mentions=mentions,
            bubble=bubble,
            keyboard=keyboard,
            opts=opts,
        )

    async def send_file(
        self,
        file: Union[TextIO, BinaryIO],
        chat_id: Union[SyncID, UUID],
        bot_id: UUID,
        host: str,
    ) -> None:
        await self._obtain_token(host, bot_id)

        response = ResponseFile(bot_id=bot_id, sync_id=chat_id).dict()

        BOTX_LOGGER.debug("sending file: %s", {"file_response": response})

        response["file"] = file

        async with self._session.post(
            self._file_url.format(host=host), data=response
        ) as resp:
            if resp.status >= 400:
                raise BotXException(
                    "unable to send file to botx",
                    data=await get_data_for_api_error_async(
                        host=host, bot_id=bot_id, response=resp, chat_ids=chat_id
                    ),
                )

    async def _obtain_token(self, host: str, bot_id: UUID) -> None:
        if self._disable_credentials:
            return

        cts = self.get_cts_by_host(host)
        if not cts:
            raise BotXException(f"unregistered cts with host {repr(host)}")

        if cts.credentials and cts.credentials.token:
            return

        signature = cts.calculate_signature(bot_id)

        BOTX_LOGGER.debug("calculated signature for %s: %s", cts.host, signature)

        async with self._session.get(
            self._token_url.format(host=host, bot_id=bot_id),
            params={"signature": signature},
        ) as resp:
            if resp.status >= 400:
                raise BotXException(
                    "unable to obtain token from botx",
                    data=await get_data_for_api_error_async(
                        host=host, bot_id=bot_id, response=resp
                    ),
                )

            token = (await resp.json()).get("result")

            cts.credentials = CTSCredentials(bot_id=bot_id, token=token)

    async def _send_command_result(
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
        opts: NotificationOpts,
    ) -> None:
        command_resp = ResponseCommand(
            bot_id=bot_id,
            sync_id=chat_id,
            command_result=ResponseResult(
                body=text, bubble=bubble, keyboard=keyboard, mentions=mentions
            ),
            recipients=recipients,
            file=file,
            opts=opts,
        )
        headers = (
            get_headers(self.get_token_from_cts(host))
            if not self._disable_credentials
            else {}
        )

        BOTX_LOGGER.debug(
            "sending command response: %s",
            {"command_response": command_resp.json(), "headers": headers},
        )

        async with self._session.post(
            self._command_url.format(host=host),
            json=command_resp.dict(),
            headers=headers,
        ) as resp:
            if resp.status >= 400:
                raise BotXException(
                    "unable to send handler result",
                    data=await get_data_for_api_error_async(
                        host=host, bot_id=bot_id, response=resp, chat_ids=chat_id
                    ),
                )

    async def _send_notification_result(
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
        opts: NotificationOpts,
    ) -> None:
        notification_resp = ResponseNotification(
            bot_id=bot_id,
            group_chat_ids=group_chat_ids,
            notification=ResponseResult(
                body=text, bubble=bubble, keyboard=keyboard, mentions=mentions
            ),
            recipients=recipients,
            file=file,
            opts=opts,
        )
        headers = (
            get_headers(self.get_token_from_cts(host))
            if not self._disable_credentials
            else {}
        )

        BOTX_LOGGER.debug(
            "sending notification response: %s",
            {"notification_response": notification_resp.json(), "headers": headers},
        )

        async with self._session.post(
            self._notification_url.format(host=host),
            json=notification_resp.dict(),
            headers=headers,
        ) as resp:
            if resp.status >= 400:
                raise BotXException(
                    "unable to send notification result",
                    data=await get_data_for_api_error_async(
                        host=host, bot_id=bot_id, response=resp, chat_ids=group_chat_ids
                    ),
                )
