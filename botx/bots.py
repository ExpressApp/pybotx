import abc
from typing import (
    Any,
    Awaitable,
    BinaryIO,
    Callable,
    Dict,
    List,
    Optional,
    TextIO,
    Type,
    Union,
)
from uuid import UUID

from .clients import AsyncBotXClient
from .collector import HandlersCollector
from .core import TEXT_MAX_LENGTH, BotXAPI, BotXException
from .dispatchers import AsyncDispatcher, BaseDispatcher
from .models import (
    CTS,
    BotCredentials,
    BotXTokenResponse,
    CommandCallback,
    CommandHandler,
    CTSCredentials,
    File,
    Message,
    MessageMarkup,
    NotifyOptions,
    ReplyMessage,
    SendingCredentials,
    SendingPayload,
    Status,
    SyncID,
)

TASKS_LIMIT = 1500


class BaseBot(abc.ABC, HandlersCollector):
    _dispatcher: BaseDispatcher
    _credentials: BotCredentials
    _token_url: str = BotXAPI.V4.token.url
    _command_url: str = BotXAPI.V4.command.url
    _notification_url: str = BotXAPI.V4.notification.url
    _file_url: str = BotXAPI.V4.file.url

    def __init__(self, *, credentials: Optional[BotCredentials] = None) -> None:
        super().__init__()

        self._credentials = credentials if credentials else BotCredentials()

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

    def start(self) -> Optional[Awaitable[None]]:
        """Run some outer dependencies that can not be started in init"""

    def stop(self) -> Optional[Awaitable[None]]:
        """Stop special objects and dispatcher for bot"""

    def exception_catcher(
        self, exceptions: List[Type[Exception]], force_replace: bool = False
    ) -> Callable:
        def _register_exception(func: Callable) -> Callable:
            for exc in exceptions:
                self._dispatcher.register_exception_catcher(
                    exc, func, force_replace=force_replace
                )

            return func

        return _register_exception

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
    def status(self) -> Union[Status, Awaitable[Status]]:
        """Get Status to bot commands menu"""

    @abc.abstractmethod
    def execute_command(self, data: Dict[str, Any]) -> Optional[Awaitable[None]]:
        """Execute handler from request"""

    @abc.abstractmethod
    def send_message(
        self,
        text: str,
        credentials: SendingCredentials,
        *,
        file: Optional[Union[BinaryIO, TextIO]] = None,
        markup: Optional[MessageMarkup] = None,
        options: Optional[NotifyOptions] = None,
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
        file: Optional[Union[BinaryIO, TextIO]] = None,
        markup: Optional[MessageMarkup] = None,
        options: Optional[NotifyOptions] = None,
    ) -> Optional[Awaitable[None]]:
        """Send message with credentials from incoming message"""

    @abc.abstractmethod
    def send_file(
        self, file: Union[TextIO, BinaryIO], credentials: SendingCredentials
    ) -> Optional[Awaitable[None]]:
        """Send separate file to BotX API"""

    @abc.abstractmethod
    def _obtain_token(
        self, credentials: SendingCredentials
    ) -> Optional[Awaitable[None]]:
        """Obtain token from BotX for making requests"""


class AsyncBot(BaseBot):
    _dispatcher: AsyncDispatcher
    _client: AsyncBotXClient

    def __init__(
        self,
        *,
        concurrent_tasks: int = TASKS_LIMIT,
        credentials: Optional[BotCredentials] = None,
    ) -> None:
        super().__init__(credentials=credentials)

        self._dispatcher = AsyncDispatcher(tasks_limit=concurrent_tasks)
        self._client = AsyncBotXClient()

    async def start(self) -> None:
        await self._dispatcher.start()

    async def stop(self) -> None:
        await self._dispatcher.shutdown()

    async def status(self) -> Status:
        return await self._dispatcher.status()

    async def execute_command(self, data: Dict[str, Any]) -> None:
        await self._dispatcher.execute_command(data)

    async def send_message(
        self,
        text: str,
        credentials: SendingCredentials,
        *,
        file: Optional[Union[BinaryIO, TextIO]] = None,
        markup: Optional[MessageMarkup] = None,
        options: Optional[NotifyOptions] = None,
    ) -> None:
        markup = markup or MessageMarkup()
        options = options or NotifyOptions()

        if len(text) > TEXT_MAX_LENGTH:
            raise BotXException(
                f"message text must be shorter {TEXT_MAX_LENGTH} symbols"
            )

        await self._obtain_token(credentials)

        payload = SendingPayload(
            text=text,
            file=File.from_file(file) if file else None,
            markup=markup,
            options=options,
        )
        if credentials.sync_id:
            await self._client.send_command_result(credentials, payload)
        elif credentials.chat_ids:
            await self._client.send_notification(credentials, payload)
        else:
            raise BotXException("both sync_id and chat_ids in credentials are missed")

    async def answer_message(
        self,
        text: str,
        message: Message,
        *,
        file: Optional[Union[BinaryIO, TextIO]] = None,
        markup: Optional[MessageMarkup] = None,
        options: Optional[NotifyOptions] = None,
    ) -> None:
        await self.send_message(
            text,
            SendingCredentials(
                sync_id=message.sync_id, bot_id=message.bot_id, host=message.host
            ),
            file=file,
            markup=markup,
            options=options,
        )

    async def reply(self, message: ReplyMessage) -> None:
        credentials = SendingCredentials(bot_id=message.bot_id, host=message.host)
        if isinstance(message.chat_id, SyncID):
            credentials.sync_id = message.chat_id
        else:
            if isinstance(message.chat_id, UUID):
                credentials.chat_ids = [message.chat_id]
            else:
                credentials.chat_ids = message.chat_id

        await self.send_message(
            message.text,
            credentials,
            file=message.file.file if message.file else None,
            markup=MessageMarkup(bubbles=message.bubble, keyboard=message.keyboard),
            options=NotifyOptions(
                recipients=message.recipients,
                mentions=message.mentions,
                notifications=message.opts,
            ),
        )

    async def send_file(
        self, file: Union[TextIO, BinaryIO], credentials: SendingCredentials
    ) -> None:
        await self._obtain_token(credentials)
        await self._client.send_file(
            credentials, SendingPayload(file=File.from_file(file))
        )

    async def _obtain_token(self, credentials: SendingCredentials) -> None:
        cts = self.get_cts_by_host(credentials.host)
        if not cts:
            raise BotXException(f"unregistered cts with host {repr(credentials.host)}")

        if cts.credentials and cts.credentials.token:
            credentials.token = cts.credentials.token
            return

        signature = cts.calculate_signature(credentials.bot_id)

        token_data = await self._client.obtain_token(
            credentials.host, credentials.bot_id, signature
        )
        token = BotXTokenResponse(**token_data).result

        cts.credentials = CTSCredentials(bot_id=credentials.bot_id, token=token)
        credentials.token = token
