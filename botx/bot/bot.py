import asyncio
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Sequence, Union
from uuid import UUID
from weakref import WeakSet

import httpx
from loguru import logger
from pydantic import ValidationError, parse_obj_as

from botx.bot.api.commands.commands import BotAPICommand
from botx.bot.api.status.recipient import BotAPIStatusRecipient
from botx.bot.api.status.response import build_bot_status_response
from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.bot.callbacks_manager import CallbacksManager
from botx.bot.contextvars import bot_id_var, bot_var, chat_id_var
from botx.bot.exceptions import AnswerDestinationLookupError
from botx.bot.handler import Middleware
from botx.bot.handler_collector import HandlerCollector
from botx.bot.middlewares.exceptions import ExceptionHandlersDict, ExceptionMiddleware
from botx.bot.models.bot_account import BotAccount
from botx.bot.models.commands.commands import BotCommand
from botx.bot.models.method_callbacks import BotXMethodCallback
from botx.bot.models.outgoing_attachment import OutgoingAttachment
from botx.bot.models.status.bot_menu import BotMenu
from botx.bot.models.status.recipient import StatusRecipient
from botx.client.chats_api.add_user import AddUserMethod, BotXAPIAddUserRequestPayload
from botx.client.chats_api.create_chat import (
    BotXAPICreateChatRequestPayload,
    CreateChatMethod,
)
from botx.client.chats_api.list_chats import ChatListItem, ListChatsMethod
from botx.client.chats_api.remove_user import (
    BotXAPIRemoveUserRequestPayload,
    RemoveUserMethod,
)
from botx.client.exceptions.common import InvalidBotAccountError
from botx.client.files_api.download_file import (
    BotXAPIDownloadFileRequestPayload,
    DownloadFileMethod,
)
from botx.client.files_api.upload_file import (
    BotXAPIUploadFileRequestPayload,
    UploadFileMethod,
)
from botx.client.get_token import get_token
from botx.client.missing import Missing, Undefined
from botx.client.notifications_api.direct_notification import (
    BotXAPIDirectNotificationRequestPayload,
    DirectNotificationMethod,
)
from botx.client.notifications_api.internal_bot_notification import (
    BotXAPIInternalBotNotificationRequestPayload,
    InternalBotNotificationMethod,
)
from botx.converters import optional_sequence_to_list
from botx.shared_models.async_buffer import AsyncBufferReadable, AsyncBufferWritable
from botx.shared_models.chat_types import ChatTypes
from botx.shared_models.domain.attachments import IncomingFileAttachment
from botx.shared_models.domain.files import File


class Bot:
    def __init__(
        self,
        *,
        collectors: Sequence[HandlerCollector],
        bot_accounts: Sequence[BotAccount],
        middlewares: Optional[Sequence[Middleware]] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        exception_handlers: Optional[ExceptionHandlersDict] = None,
    ) -> None:
        if not collectors:
            logger.warning("Bot has no connected collectors")
        if not bot_accounts:
            logger.warning("Bot has no bot accounts")

        self.state: SimpleNamespace = SimpleNamespace()

        self._middlewares = optional_sequence_to_list(middlewares)
        self._add_exception_middleware(exception_handlers)

        self._handler_collector = self._merge_collectors(collectors)

        self._bot_accounts_storage = BotAccountsStorage(list(bot_accounts))
        self._httpx_client = httpx_client or httpx.AsyncClient()

        self._tasks: "WeakSet[asyncio.Task[None]]" = WeakSet()

        self._callback_manager = CallbacksManager()

    def async_execute_raw_bot_command(self, raw_bot_command: Dict[str, Any]) -> None:
        try:
            bot_api_command: BotAPICommand = parse_obj_as(
                # Same ignore as in pydantic
                BotAPICommand,  # type: ignore[arg-type]
                raw_bot_command,
            )
        except ValidationError as validation_exc:
            raise ValueError("Bot command validation error") from validation_exc

        self._fill_contextvars(bot_api_command)

        bot_command = bot_api_command.to_domain(raw_bot_command)
        self.async_execute_bot_command(bot_command)

    def async_execute_bot_command(self, bot_command: BotCommand) -> None:
        task = asyncio.create_task(
            self._handler_collector.handle_bot_command(bot_command, self),
        )
        self._tasks.add(task)

    async def raw_get_status(self, query_params: Dict[str, str]) -> Dict[str, Any]:
        try:
            bot_api_status_recipient = BotAPIStatusRecipient.parse_obj(query_params)
        except ValidationError as exc:
            raise ValueError("Status request validation error") from exc

        status_recipient = bot_api_status_recipient.to_domain()

        bot_menu = await self.get_status(status_recipient)
        return build_bot_status_response(bot_menu)

    async def get_status(self, status_recipient: StatusRecipient) -> BotMenu:
        return await self._handler_collector.get_bot_menu(status_recipient, self)

    def set_raw_botx_method_result(
        self,
        raw_botx_method_result: Dict[str, Any],
    ) -> None:
        callback: BotXMethodCallback = parse_obj_as(
            # Same ignore as in pydantic
            BotXMethodCallback,  # type: ignore[arg-type]
            raw_botx_method_result,
        )
        self._callback_manager.set_botx_method_callback_result(callback)

    async def startup(self) -> None:
        for host, bot_id in self._bot_accounts_storage.iter_host_and_bot_id_pairs():
            try:
                token = await self.get_token(bot_id)
            except (InvalidBotAccountError, httpx.HTTPError):
                logger.warning(
                    "Can't get token for bot account: "
                    f"host - {host}, bot_id - {bot_id}",
                )
                continue

            self._bot_accounts_storage.set_token(bot_id, token)

    async def shutdown(self) -> None:
        await self._httpx_client.aclose()
        self._callback_manager.stop_callbacks_waiting()

        if not self._tasks:
            return

        finished_tasks, _ = await asyncio.wait(
            self._tasks,
            return_when=asyncio.ALL_COMPLETED,
        )

        # Raise handlers exceptions
        for task in finished_tasks:
            task.result()

    # - Bots API -
    async def get_token(self, bot_id: UUID) -> str:
        """Get bot auth token.

        **Arguments:**

        * `bot_id: UUID` - Bot which should perform the request.

        **Returns:**

        `str` - Auth token.
        """

        return await get_token(bot_id, self._httpx_client, self._bot_accounts_storage)

    # - Chats API -
    async def list_chats(
        self,
        bot_id: UUID,
    ) -> List[ChatListItem]:
        """Get all bot chats.

        **Arguments:**

        * `bot_id: UUID` - Bot which should perform the request.

        **Returns:**

        `List[ChatListItem]` - List of chats info.
        """

        method = ListChatsMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        botx_api_list_chat = await method.execute()

        return botx_api_list_chat.to_domain()

    async def add_user_to_chat(
        self,
        bot_id: UUID,
        chat_id: UUID,
        huids: List[UUID],
    ) -> None:
        """Add user to chat.

        **Arguments:**

        * `bot_id: UUID` - Bot which should perform the request.
        * `chat_id: UUID` - Target chat id.
        * `huids: List[UUID]` - List of eXpress account ids.
        """

        method = AddUserMethod(bot_id, self._httpx_client, self._bot_accounts_storage)

        payload = BotXAPIAddUserRequestPayload.from_domain(chat_id, huids)
        await method.execute(payload)

    async def remove_users_from_chat(
        self,
        bot_id: UUID,
        chat_id: UUID,
        huids: List[UUID],
    ) -> None:
        """Remove eXpress accounts from chat.

        **Arguments:**

        * `bot_id: UUID` - Bot which should perform the request.
        * `chat_id: UUID` - Target chat id.
        * `huids: List[UUID]` - List of eXpress account ids.
        """

        method = RemoveUserMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPIRemoveUserRequestPayload.from_domain(chat_id, huids)
        await method.execute(payload)

    async def create_chat(
        self,
        bot_id: UUID,
        name: str,
        chat_type: ChatTypes,
        huids: List[UUID],
        description: Optional[str] = None,
        shared_history: bool = False,
    ) -> UUID:
        """Create chat.

        **Arguments:**

        * `bot_id: UUID` - Bot which should perform the request.
        * `name: str` - Chat visible name.
        * `chat_type: ChatTypes` - Chat type.
        * `huids: List[UUID]` - List of eXpress account ids.
        * `description: Optional[str]` - Chat description.
        * `shared_history: bool` - Open old chat history for new added users.

        **Returns:**

        `UUID` - Created chat uuid.
        """

        method = CreateChatMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPICreateChatRequestPayload.from_domain(
            name,
            chat_type,
            huids,
            description,
            shared_history,
        )
        botx_api_chat_id = await method.execute(payload)

        return botx_api_chat_id.to_domain()

    # - Notifications API-
    async def answer(
        self,
        body: str,
        *,
        metadata: Missing[Dict[str, Any]] = Undefined,
        file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined,
    ) -> UUID:
        """Answer to incoming message.

        Works just like `Bot.send`, but `bot_id` and `chat_id` are
        taken from the incoming message.

        **Arguments:**

        * `metadata: Missing[Dict[str, Any]]` - Notification options.
        * `file: Missing[Union[IncomingFileAttachment,
        OutgoingAttachment]]` - Attachment.

        **Returns:**

        `UUID` - Notification sync_id.
        """

        try:  # noqa: WPS229
            bot_id = bot_id_var.get()
            chat_id = chat_id_var.get()
        except LookupError as exc:
            raise AnswerDestinationLookupError from exc

        return await self.send(
            body,
            bot_id=bot_id,
            chat_id=chat_id,
            metadata=metadata,
            file=file,
        )

    async def send(
        self,
        body: str,
        *,
        bot_id: UUID,
        chat_id: UUID,
        metadata: Missing[Dict[str, Any]] = Undefined,
        file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined,
    ) -> UUID:
        """Send message to chat.

        **Arguments:**

        * `bot_id: UUID` - Bot which should perform the request.
        * `chat_id: UUID` - Target chat id.
        * `metadata: Missing[Dict[str, Any]]` - Notification options.
        * `file: Missing[Union[IncomingFileAttachment,
        OutgoingAttachment]]` - Attachment.

        **Returns:**

        `UUID` - Notification sync_id.
        """

        method = DirectNotificationMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPIDirectNotificationRequestPayload.from_domain(
            chat_id,
            body,
            metadata,
            file,
        )
        botx_api_sync_id = await method.execute(payload)

        return botx_api_sync_id.to_domain()

    async def send_internal_bot_notification(
        self,
        bot_id: UUID,
        chat_id: UUID,
        data: Dict[str, Any],
        opts: Missing[Dict[str, Any]] = Undefined,
        recipients: Missing[List[UUID]] = Undefined,
        wait_callback: bool = True,
        callback_timeout: Optional[int] = None,
    ) -> UUID:
        """Send internal notification.

        **Arguments:**

        * `bot_id: UUID` - Bot which should perform the request.
        * `chat_id: UUID` - Target chat id.
        * `data: Dict[str, Any]` - Notification payload.
        * `opts: Missing[Dict[str, Any]]` - Notification options.
        * `recipients: Missing[List[UUID]]` - List of bot uuids, empty for all in chat.
        * `wait_callback: bool` - Wait for callback.
        * `callback_timeout: Optional[int]` - Timeout for waiting for callback.

        **Returns:**

        `UUID` - Notification sync_id.
        """

        method = InternalBotNotificationMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
            self._callback_manager,
        )

        payload = BotXAPIInternalBotNotificationRequestPayload.from_domain(
            chat_id,
            data,
            opts,
            recipients,
        )
        botx_api_sync_id = await method.execute(
            payload,
            wait_callback,
            callback_timeout,
        )

        return botx_api_sync_id.to_domain()

    # - Files API -
    async def download_file(
        self,
        bot_id: UUID,
        chat_id: UUID,
        file_id: UUID,
        async_buffer: AsyncBufferWritable,
    ) -> None:
        """Download file form file service.

        **Arguments:**

        * `bot_id: UUID` - Bot which should perform the request.
        * `chat_id: UUID` - Target chat id.
        * `file_id: UUID` - Async file id.
        * `async_buffer: AsyncBufferWritable` - Buffer to write downloaded file.
        """

        payload = BotXAPIDownloadFileRequestPayload.from_domain(chat_id, file_id)
        method = DownloadFileMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        await method.execute(payload, async_buffer)

    async def upload_file(
        self,
        bot_id: UUID,
        chat_id: UUID,
        async_buffer: AsyncBufferReadable,
        filename: str,
        duration: Missing[int] = Undefined,
        caption: Missing[str] = Undefined,
    ) -> File:
        """Upload file to file service.

        **Arguments:**

        * `bot_id: UUID` - Bot which should perform the request.
        * `chat_id: UUID` - Target chat id.
        * `file_id: UUID` - Async file id.
        * `async_buffer: AsyncBufferReadable` - Buffer to write downloaded file.
        * `filename: str` - File name.
        * `duration: Missing[str]` - Video duration.
        * `caption: Missing[str]` - Text under file.

        **Returns:**

        * `File` - Meta info of uploaded file.
        """

        payload = BotXAPIUploadFileRequestPayload.from_domain(
            chat_id,
            duration,
            caption,
        )
        method = UploadFileMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        api_async_file = await method.execute(payload, async_buffer, filename)

        return api_async_file.to_domain()

    def _add_exception_middleware(
        self,
        exception_handlers: Optional[ExceptionHandlersDict] = None,
    ) -> None:
        exception_middleware = ExceptionMiddleware(exception_handlers or {})
        self._middlewares.insert(0, exception_middleware.dispatch)

    def _merge_collectors(
        self,
        collectors: Sequence[HandlerCollector],
    ) -> HandlerCollector:
        main_collector = HandlerCollector(middlewares=self._middlewares)
        main_collector.include(*collectors)

        return main_collector

    def _fill_contextvars(self, bot_api_command: BotAPICommand) -> None:
        bot_var.set(self)
        bot_id_var.set(bot_api_command.bot_id)
        chat_id_var.set(bot_api_command.sender.group_chat_id)
