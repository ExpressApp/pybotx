from asyncio import Task
from types import SimpleNamespace
from typing import Any, AsyncIterable, Dict, Iterator, List, Optional, Sequence, Union
from uuid import UUID

import httpx
from pydantic import ValidationError, parse_obj_as

from pybotx.async_buffer import AsyncBufferReadable, AsyncBufferWritable
from pybotx.bot.bot_accounts_storage import BotAccountsStorage
from pybotx.bot.callbacks.callback_manager import CallbackManager
from pybotx.bot.callbacks.callback_memory_repo import CallbackMemoryRepo
from pybotx.bot.callbacks.callback_repo_proto import CallbackRepoProto
from pybotx.bot.contextvars import bot_id_var, chat_id_var
from pybotx.bot.exceptions import AnswerDestinationLookupError
from pybotx.bot.handler import Middleware
from pybotx.bot.handler_collector import HandlerCollector
from pybotx.bot.middlewares.exception_middleware import ExceptionHandlersDict
from pybotx.client.chats_api.add_admin import (
    AddAdminMethod,
    BotXAPIAddAdminRequestPayload,
)
from pybotx.client.chats_api.add_user import AddUserMethod, BotXAPIAddUserRequestPayload
from pybotx.client.chats_api.chat_info import (
    BotXAPIChatInfoRequestPayload,
    ChatInfoMethod,
)
from pybotx.client.chats_api.create_chat import (
    BotXAPICreateChatRequestPayload,
    CreateChatMethod,
)
from pybotx.client.chats_api.disable_stealth import (
    BotXAPIDisableStealthRequestPayload,
    DisableStealthMethod,
)
from pybotx.client.chats_api.list_chats import ListChatsMethod
from pybotx.client.chats_api.pin_message import (
    BotXAPIPinMessageRequestPayload,
    PinMessageMethod,
)
from pybotx.client.chats_api.remove_user import (
    BotXAPIRemoveUserRequestPayload,
    RemoveUserMethod,
)
from pybotx.client.chats_api.set_stealth import (
    BotXAPISetStealthRequestPayload,
    SetStealthMethod,
)
from pybotx.client.chats_api.unpin_message import (
    BotXAPIUnpinMessageRequestPayload,
    UnpinMessageMethod,
)
from pybotx.client.events_api.edit_event import (
    BotXAPIEditEventRequestPayload,
    EditEventMethod,
)
from pybotx.client.events_api.message_status_event import (
    BotXAPIMessageStatusRequestPayload,
    MessageStatusMethod,
)
from pybotx.client.events_api.reply_event import (
    BotXAPIReplyEventRequestPayload,
    ReplyEventMethod,
)
from pybotx.client.events_api.stop_typing_event import (
    BotXAPIStopTypingEventRequestPayload,
    StopTypingEventMethod,
)
from pybotx.client.events_api.typing_event import (
    BotXAPITypingEventRequestPayload,
    TypingEventMethod,
)
from pybotx.client.exceptions.common import InvalidBotAccountError
from pybotx.client.files_api.download_file import (
    BotXAPIDownloadFileRequestPayload,
    DownloadFileMethod,
)
from pybotx.client.files_api.upload_file import (
    BotXAPIUploadFileRequestPayload,
    UploadFileMethod,
)
from pybotx.client.get_token import get_token
from pybotx.client.notifications_api.direct_notification import (
    BotXAPIDirectNotificationRequestPayload,
    DirectNotificationMethod,
)
from pybotx.client.notifications_api.internal_bot_notification import (
    BotXAPIInternalBotNotificationRequestPayload,
    InternalBotNotificationMethod,
)
from pybotx.client.smartapps_api.smartapp_event import (
    BotXAPISmartAppEventRequestPayload,
    SmartAppEventMethod,
)
from pybotx.client.smartapps_api.smartapp_notification import (
    BotXAPISmartAppNotificationRequestPayload,
    SmartAppNotificationMethod,
)
from pybotx.client.stickers_api.add_sticker import (
    AddStickerMethod,
    BotXAPIAddStickerRequestPayload,
)
from pybotx.client.stickers_api.create_sticker_pack import (
    BotXAPICreateStickerPackRequestPayload,
    CreateStickerPackMethod,
)
from pybotx.client.stickers_api.delete_sticker import (
    BotXAPIDeleteStickerRequestPayload,
    DeleteStickerMethod,
)
from pybotx.client.stickers_api.delete_sticker_pack import (
    BotXAPIDeleteStickerPackRequestPayload,
    DeleteStickerPackMethod,
)
from pybotx.client.stickers_api.edit_sticker_pack import (
    BotXAPIEditStickerPackRequestPayload,
    EditStickerPackMethod,
)
from pybotx.client.stickers_api.get_sticker import (
    BotXAPIGetStickerRequestPayload,
    GetStickerMethod,
)
from pybotx.client.stickers_api.get_sticker_pack import (
    BotXAPIGetStickerPackRequestPayload,
    GetStickerPackMethod,
)
from pybotx.client.stickers_api.get_sticker_packs import (
    BotXAPIGetStickerPacksRequestPayload,
    GetStickerPacksMethod,
)
from pybotx.client.users_api.search_user_by_email import (
    BotXAPISearchUserByEmailRequestPayload,
    SearchUserByEmailMethod,
)
from pybotx.client.users_api.search_user_by_huid import (
    BotXAPISearchUserByHUIDRequestPayload,
    SearchUserByHUIDMethod,
)
from pybotx.client.users_api.search_user_by_login import (
    BotXAPISearchUserByLoginRequestPayload,
    SearchUserByLoginMethod,
)
from pybotx.client.users_api.search_user_by_other_id import (
    BotXAPISearchUserByOtherIdRequestPayload,
    SearchUserByOtherIdMethod,
)
from pybotx.client.users_api.update_user_profile import (
    BotXAPIUpdateUserProfileRequestPayload,
    UpdateUsersProfileMethod,
)
from pybotx.constants import BOTX_DEFAULT_TIMEOUT, STICKER_PACKS_PER_PAGE
from pybotx.converters import optional_sequence_to_list
from pybotx.image_validators import (
    ensure_file_content_is_png,
    ensure_sticker_image_size_valid,
)
from pybotx.logger import logger, pformat_jsonable_obj, trim_file_data_in_incoming_json
from pybotx.missing import Missing, MissingOptional, Undefined
from pybotx.models.async_files import File
from pybotx.models.attachments import IncomingFileAttachment, OutgoingAttachment
from pybotx.models.bot_account import BotAccount, BotAccountWithSecret
from pybotx.models.chats import ChatInfo, ChatListItem
from pybotx.models.commands import BotAPICommand, BotCommand
from pybotx.models.enums import ChatTypes
from pybotx.models.message.edit_message import EditMessage
from pybotx.models.message.markup import BubbleMarkup, KeyboardMarkup
from pybotx.models.message.message_status import MessageStatus
from pybotx.models.message.outgoing_message import OutgoingMessage
from pybotx.models.message.reply_message import ReplyMessage
from pybotx.models.method_callbacks import BotXMethodCallback
from pybotx.models.status import (
    BotAPIStatusRecipient,
    BotMenu,
    StatusRecipient,
    build_bot_status_response,
)
from pybotx.models.stickers import Sticker, StickerPack, StickerPackFromList
from pybotx.models.users import UserFromSearch

MissingOptionalAttachment = MissingOptional[
    Union[IncomingFileAttachment, OutgoingAttachment]
]


class Bot:
    def __init__(
        self,
        *,
        collectors: Sequence[HandlerCollector],
        bot_accounts: Sequence[BotAccountWithSecret],
        middlewares: Optional[Sequence[Middleware]] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        exception_handlers: Optional[ExceptionHandlersDict] = None,
        default_callback_timeout: float = BOTX_DEFAULT_TIMEOUT,
        callback_repo: Optional[CallbackRepoProto] = None,
    ) -> None:
        if not collectors:
            logger.warning("Bot has no connected collectors")
        if not bot_accounts:
            logger.warning("Bot has no bot accounts")

        middlewares = optional_sequence_to_list(middlewares)
        self._handler_collector = self._build_main_collector(
            collectors,
            middlewares,
            exception_handlers,
        )

        self._default_callback_timeout = default_callback_timeout
        self._bot_accounts_storage = BotAccountsStorage(list(bot_accounts))
        self._httpx_client = httpx_client or httpx.AsyncClient()

        if not callback_repo:
            callback_repo = CallbackMemoryRepo()

        self._callbacks_manager = CallbackManager(callback_repo)

        self.state: SimpleNamespace = SimpleNamespace()

    def async_execute_raw_bot_command(self, raw_bot_command: Dict[str, Any]) -> None:
        logger.opt(lazy=True).debug(
            "Got command: {command}",
            command=lambda: pformat_jsonable_obj(
                trim_file_data_in_incoming_json(raw_bot_command),
            ),
        )

        try:
            bot_api_command: BotAPICommand = parse_obj_as(
                # Same ignore as in pydantic
                BotAPICommand,  # type: ignore[arg-type]
                raw_bot_command,
            )
        except ValidationError as validation_exc:
            raise ValueError("Bot command validation error") from validation_exc

        bot_command = bot_api_command.to_domain(raw_bot_command)
        self.async_execute_bot_command(bot_command)

    def async_execute_bot_command(
        self,
        bot_command: BotCommand,
    ) -> "Task[None]":
        # raise UnknownBotAccountError if no bot account with this bot_id.
        self._bot_accounts_storage.ensure_bot_id_exists(bot_command.bot.id)

        return self._handler_collector.async_handle_bot_command(self, bot_command)

    async def raw_get_status(self, query_params: Dict[str, str]) -> Dict[str, Any]:
        logger.opt(lazy=True).debug(
            "Got status: {status}",
            status=lambda: pformat_jsonable_obj(query_params),
        )

        try:
            bot_api_status_recipient = BotAPIStatusRecipient.parse_obj(query_params)
        except ValidationError as exc:
            raise ValueError("Status request validation error") from exc

        status_recipient = bot_api_status_recipient.to_domain()

        bot_menu = await self.get_status(status_recipient)
        return build_bot_status_response(bot_menu)

    async def get_status(self, status_recipient: StatusRecipient) -> BotMenu:
        # raise UnknownBotAccountError if no bot account with this bot_id.
        self._bot_accounts_storage.ensure_bot_id_exists(status_recipient.bot_id)

        return await self._handler_collector.get_bot_menu(status_recipient, self)

    async def set_raw_botx_method_result(
        self,
        raw_botx_method_result: Dict[str, Any],
    ) -> None:
        logger.debug("Got callback: {callback}", callback=raw_botx_method_result)

        callback: BotXMethodCallback = parse_obj_as(
            # Same ignore as in pydantic
            BotXMethodCallback,  # type: ignore[arg-type]
            raw_botx_method_result,
        )

        await self._callbacks_manager.set_botx_method_callback_result(callback)

    async def wait_botx_method_callback(
        self,
        sync_id: UUID,
    ) -> BotXMethodCallback:
        timeout = self._callbacks_manager.cancel_callback_timeout_alarm(
            sync_id,
            return_remaining_time=True,
        )

        return await self._callbacks_manager.wait_botx_method_callback(sync_id, timeout)

    @property
    def bot_accounts(self) -> Iterator[BotAccount]:
        yield from self._bot_accounts_storage.iter_bot_accounts()

    async def fetch_tokens(self) -> None:
        for bot_account in self.bot_accounts:
            try:
                token = await self.get_token(bot_id=bot_account.id)
            except (InvalidBotAccountError, httpx.HTTPError):
                logger.warning(
                    "Can't get token for bot account: "
                    f"host - {bot_account.host}, bot_id - {bot_account.id}",
                )
                continue

            self._bot_accounts_storage.set_token(bot_account.id, token)

    async def startup(self, *, fetch_tokens: bool = True) -> None:
        if fetch_tokens:
            await self.fetch_tokens()

    async def shutdown(self) -> None:
        await self._callbacks_manager.stop_callbacks_waiting()
        await self._handler_collector.wait_active_tasks()
        await self._httpx_client.aclose()

    # - Bots API -
    async def get_token(
        self,
        *,
        bot_id: UUID,
    ) -> str:
        """Get bot auth token.

        :param bot_id: Bot which should perform the request.

        :return: Auth token.
        """

        return await get_token(bot_id, self._httpx_client, self._bot_accounts_storage)

    # - Notifications API -
    async def answer_message(
        self,
        body: str,
        *,
        metadata: Missing[Dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined,
        recipients: Missing[List[UUID]] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
        wait_callback: bool = True,
        callback_timeout: Optional[float] = None,
    ) -> UUID:
        """Answer to incoming message.

        Works just like `Bot.send`, but `bot_id` and `chat_id` are
        taken from the incoming message.

        :param body: Message body.
        :param metadata: Notification options.
        :param bubbles: Bubbles (buttons attached to message) markup.
        :param keyboard: Keyboard (buttons below message input) markup.
        :param file: Attachment.
        :param recipients: List of recipients, empty for all in chat.
        :param silent_response: (BotX default: False) Exclude next user
            messages from history.
        :param markup_auto_adjust: (BotX default: False) Move button to next
            row, if its text doesn't fit.
        :param stealth_mode: (BotX default: False) Enable stealth mode.
        :param send_push: (BotX default: True) Send push notification on
            devices.
        :param ignore_mute: (BotX default: False) Ignore mute or dnd (do not
            disturb).
        :param wait_callback: Block method call until callback received.
        :param callback_timeout: Callback timeout in seconds (or `None` for
            endless waiting).

        :raises AnswerDestinationLookupError: If you try to answer without
            receiving incoming message.

        :return: Notification sync_id.
        """

        try:  # noqa: WPS229
            bot_id = bot_id_var.get()
            chat_id = chat_id_var.get()
        except LookupError as exc:
            raise AnswerDestinationLookupError from exc

        return await self.send_message(
            bot_id=bot_id,
            chat_id=chat_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            recipients=recipients,
            silent_response=silent_response,
            markup_auto_adjust=markup_auto_adjust,
            stealth_mode=stealth_mode,
            send_push=send_push,
            ignore_mute=ignore_mute,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )

    async def send(
        self,
        *,
        message: OutgoingMessage,
        wait_callback: bool = True,
        callback_timeout: Optional[float] = None,
    ) -> UUID:
        """Send internal notification.

        :param message: Built outgoing message.
        :param wait_callback: Wait for callback.
        :param callback_timeout: Timeout for waiting for callback.

        :return: Notification sync_id.
        """

        return await self.send_message(
            bot_id=message.bot_id,
            chat_id=message.chat_id,
            body=message.body,
            metadata=message.metadata,
            bubbles=message.bubbles,
            keyboard=message.keyboard,
            file=message.file,
            recipients=message.recipients,
            silent_response=message.silent_response,
            markup_auto_adjust=message.markup_auto_adjust,
            stealth_mode=message.stealth_mode,
            send_push=message.send_push,
            ignore_mute=message.ignore_mute,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )

    async def send_message(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        body: str,
        metadata: Missing[Dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        recipients: Missing[List[UUID]] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
        wait_callback: bool = True,
        callback_timeout: Optional[float] = None,
    ) -> UUID:
        """Send message to chat.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param body: Message body.
        :param metadata: Notification options.
        :param bubbles: Bubbles (buttons attached to message) markup.
        :param keyboard: Keyboard (buttons below message input) markup.
        :param file: Attachment.
        :param recipients: List of recipients, empty for all in chat.
        :param silent_response: (BotX default: False) Exclude next user
            messages from history.
        :param markup_auto_adjust: (BotX default: False) Move button to next
            row, if its text doesn't fit.
        :param stealth_mode: (BotX default: False) Enable stealth mode.
        :param send_push: (BotX default: True) Send push notification on
            devices.
        :param ignore_mute: (BotX default: False) Ignore mute or dnd (do not
            disturb).
        :param wait_callback: Block method call until callback received.
        :param callback_timeout: Callback timeout in seconds (or `None` for
            endless waiting).

        :return: Notification sync_id.
        """

        method = DirectNotificationMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
            self._callbacks_manager,
        )

        payload = BotXAPIDirectNotificationRequestPayload.from_domain(
            chat_id=chat_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            recipients=recipients,
            silent_response=silent_response,
            markup_auto_adjust=markup_auto_adjust,
            stealth_mode=stealth_mode,
            send_push=send_push,
            ignore_mute=ignore_mute,
        )
        botx_api_sync_id = await method.execute(
            payload,
            wait_callback,
            callback_timeout,
            self._default_callback_timeout,
        )

        return botx_api_sync_id.to_domain()

    async def send_internal_bot_notification(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        data: Dict[str, Any],
        opts: Missing[Dict[str, Any]] = Undefined,
        recipients: Missing[List[UUID]] = Undefined,
        wait_callback: bool = True,
        callback_timeout: Optional[float] = None,
    ) -> UUID:
        """Send internal notification.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param data: Notification payload.
        :param opts: Notification options.
        :param recipients: List of bot uuids, empty for all in chat.
        :param wait_callback: Wait for callback.
        :param callback_timeout: Timeout for waiting for callback.

        :return: Notification sync_id.
        """

        method = InternalBotNotificationMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
            self._callbacks_manager,
        )

        payload = BotXAPIInternalBotNotificationRequestPayload.from_domain(
            chat_id=chat_id,
            data=data,
            opts=opts,
            recipients=recipients,
        )
        botx_api_sync_id = await method.execute(
            payload,
            wait_callback,
            callback_timeout,
            self._default_callback_timeout,
        )

        return botx_api_sync_id.to_domain()

    # - Events API -
    async def edit(
        self,
        *,
        message: EditMessage,
    ) -> None:
        """Edit message.

        :param message: Built outgoing edit message.
        """

        await self.edit_message(
            bot_id=message.bot_id,
            sync_id=message.sync_id,
            body=message.body,
            metadata=message.metadata,
            bubbles=message.bubbles,
            keyboard=message.keyboard,
            file=message.file,
            markup_auto_adjust=message.markup_auto_adjust,
        )

    async def edit_message(
        self,
        *,
        bot_id: UUID,
        sync_id: UUID,
        body: Missing[str] = Undefined,
        metadata: Missing[Dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: MissingOptionalAttachment = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
    ) -> None:
        """Edit message.

        :param bot_id: Bot which should perform the request.
        :param sync_id: `sync_id` of message to update.
        :param body: New message body. Skip to leave previous body or pass
            empty string to clean it.
        :param metadata: Notification options. Skip to leave previous metadata.
        :param bubbles: Bubbles (buttons attached to message) markup. Skip to
            leave previous bubbles.
        :param keyboard: Keyboard (buttons below message input) markup. Skip
            to leave previous keyboard.
        :param file: Attachment. Skip to leave previous file or pass `None`
            to clean it.
        :param markup_auto_adjust: (BotX default: False) Move button to next
            row, if its text doesn't fit.
        """

        method = EditEventMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIEditEventRequestPayload.from_domain(
            sync_id=sync_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            markup_auto_adjust=markup_auto_adjust,
        )

        await method.execute(payload)

    async def reply(
        self,
        *,
        message: ReplyMessage,
    ) -> None:
        """Reply message.

        :param message: Built outgoing reply message.
        """

        await self.reply_message(
            bot_id=message.bot_id,
            sync_id=message.sync_id,
            body=message.body,
            metadata=message.metadata,
            bubbles=message.bubbles,
            keyboard=message.keyboard,
            file=message.file,
            silent_response=message.silent_response,
            markup_auto_adjust=message.markup_auto_adjust,
            stealth_mode=message.stealth_mode,
            send_push=message.send_push,
            ignore_mute=message.ignore_mute,
        )

    async def reply_message(
        self,
        *,
        bot_id: UUID,
        sync_id: UUID,
        body: str,
        metadata: Missing[Dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
    ) -> None:
        """Reply on message by `sync_id`.

        :param bot_id: Bot which should perform the request.
        :param sync_id: `sync_id` of message to reply on.
        :param body: Reply body.
        :param metadata: Notification options.
        :param bubbles: Bubbles (buttons attached to message) markup.
        :param keyboard: Keyboard (buttons below message input) markup.
        :param file: Attachment.
        :param silent_response: (BotX default: False) Exclude next user
            messages from history.
        :param markup_auto_adjust: (BotX default: False) Move button to next
            row, if its text doesn't fit.
        :param stealth_mode: (BotX default: False) Enable stealth mode.
        :param send_push: (BotX default: True) Send push notification on
            devices.
        :param ignore_mute: (BotX default: False) Ignore mute or dnd (do not
            disturb).
        """

        payload = BotXAPIReplyEventRequestPayload.from_domain(
            sync_id=sync_id,
            body=body,
            metadata=metadata,
            bubbles=bubbles,
            keyboard=keyboard,
            file=file,
            silent_response=silent_response,
            markup_auto_adjust=markup_auto_adjust,
            stealth_mode=stealth_mode,
            send_push=send_push,
            ignore_mute=ignore_mute,
        )
        method = ReplyEventMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        await method.execute(payload)

    async def get_message_status(self, *, bot_id: UUID, sync_id: UUID) -> MessageStatus:
        """
        Get status of message by `sync_id`.

        :param bot_id: Bot which should perform the request.
        :param sync_id: `sync_id` of message to get its status.

        :returns: Message status object.
        """
        payload = BotXAPIMessageStatusRequestPayload.from_domain(sync_id=sync_id)
        method = MessageStatusMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        botx_api_message_status = await method.execute(payload)
        return botx_api_message_status.to_domain()

    async def start_typing(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> None:
        """Send `typing` event.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        """

        payload = BotXAPITypingEventRequestPayload.from_domain(
            chat_id=chat_id,
        )
        method = TypingEventMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        await method.execute(payload)

    async def stop_typing(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> None:
        """Send `stop_typing` event.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        """

        payload = BotXAPIStopTypingEventRequestPayload.from_domain(
            chat_id=chat_id,
        )
        method = StopTypingEventMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        await method.execute(payload)

    # - Chats API -
    async def list_chats(
        self,
        *,
        bot_id: UUID,
    ) -> List[ChatListItem]:
        """Get all bot chats.

        :param bot_id: Bot which should perform the request.

        :returns: List of chats info.
        """

        method = ListChatsMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        botx_api_list_chat = await method.execute()

        return botx_api_list_chat.to_domain()

    async def chat_info(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> ChatInfo:
        """Get chat information.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.

        :return: Chat information.
        """

        method = ChatInfoMethod(bot_id, self._httpx_client, self._bot_accounts_storage)

        payload = BotXAPIChatInfoRequestPayload.from_domain(chat_id=chat_id)
        botx_api_chat_info = await method.execute(payload)

        return botx_api_chat_info.to_domain()

    async def add_users_to_chat(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: List[UUID],
    ) -> None:
        """Add user to chat.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param huids: List of eXpress account ids.
        """

        method = AddUserMethod(bot_id, self._httpx_client, self._bot_accounts_storage)

        payload = BotXAPIAddUserRequestPayload.from_domain(chat_id=chat_id, huids=huids)
        await method.execute(payload)

    async def remove_users_from_chat(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: List[UUID],
    ) -> None:
        """Remove eXpress accounts from chat.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param huids: List of eXpress account ids.
        """

        method = RemoveUserMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPIRemoveUserRequestPayload.from_domain(
            chat_id=chat_id,
            huids=huids,
        )
        await method.execute(payload)

    async def promote_to_chat_admins(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: List[UUID],
    ) -> None:
        """Promote users in chat to admins.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param huids: List of eXpress account ids.
        """

        method = AddAdminMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPIAddAdminRequestPayload.from_domain(
            chat_id=chat_id,
            huids=huids,
        )
        await method.execute(payload)

    async def enable_stealth(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        disable_web_client: Missing[bool] = Undefined,
        ttl_after_read: Missing[int] = Undefined,
        total_ttl: Missing[int] = Undefined,
    ) -> None:
        """Enable stealth mode.

        After the expiration of the time all messages will be hidden.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param disable_web_client: (BotX default: False) Should messages
            be shown in web.
        :param ttl_after_read: (BotX default: OFF) Time of messages burning
            after read.
        :param total_ttl: (BotX default: OFF) Time of messages burning after
            send.
        """

        method = SetStealthMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISetStealthRequestPayload.from_domain(
            chat_id=chat_id,
            disable_web_client=disable_web_client,
            ttl_after_read=ttl_after_read,
            total_ttl=total_ttl,
        )

        await method.execute(payload)

    async def disable_stealth(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> None:
        """Disable stealth model. Hides all messages that were in stealth.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        """

        method = DisableStealthMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIDisableStealthRequestPayload.from_domain(chat_id=chat_id)

        await method.execute(payload)

    async def create_chat(
        self,
        *,
        bot_id: UUID,
        name: str,
        chat_type: ChatTypes,
        huids: List[UUID],
        description: Optional[str] = None,
        shared_history: Missing[bool] = Undefined,
    ) -> UUID:
        """Create chat.

        :param bot_id: Bot which should perform the request.
        :param name: Chat visible name.
        :param chat_type: Chat type.
        :param huids: List of eXpress account ids.
        :param description: Chat description.
        :param shared_history: (BotX default: False) Open old chat history for
            new added users.

        :return: Created chat uuid.
        """

        method = CreateChatMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPICreateChatRequestPayload.from_domain(
            name=name,
            chat_type=chat_type,
            huids=huids,
            shared_history=shared_history,
            description=description,
        )
        botx_api_chat_id = await method.execute(payload)

        return botx_api_chat_id.to_domain()

    async def pin_message(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        sync_id: UUID,
    ) -> None:
        """Pin message in chat.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param sync_id: Target sync id.
        """

        method = PinMessageMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIPinMessageRequestPayload.from_domain(
            chat_id=chat_id,
            sync_id=sync_id,
        )

        await method.execute(payload)

    async def unpin_message(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> None:
        """Unpin message in chat.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        """

        method = UnpinMessageMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIUnpinMessageRequestPayload.from_domain(chat_id=chat_id)

        await method.execute(payload)

    # - Users API -
    async def search_user_by_email(
        self,
        *,
        bot_id: UUID,
        email: str,
    ) -> UserFromSearch:
        """Search user by email for search.

        :param bot_id: Bot which should perform the request.
        :param email: User email.

        :return: User information.
        """

        method = SearchUserByEmailMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISearchUserByEmailRequestPayload.from_domain(email=email)

        botx_api_user_from_search = await method.execute(payload)

        return botx_api_user_from_search.to_domain()

    async def search_user_by_huid(
        self,
        *,
        bot_id: UUID,
        huid: UUID,
    ) -> UserFromSearch:
        """Search user by huid for search.

        :param bot_id: Bot which should perform the request.
        :param huid: User huid.

        :return: User information.
        """

        method = SearchUserByHUIDMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISearchUserByHUIDRequestPayload.from_domain(huid=huid)

        botx_api_user_from_search = await method.execute(payload)

        return botx_api_user_from_search.to_domain()

    async def search_user_by_ad(
        self,
        *,
        bot_id: UUID,
        ad_login: str,
        ad_domain: str,
    ) -> UserFromSearch:
        """Search user by AD login and AD domain for search.

        :param bot_id: Bot which should perform the request.
        :param ad_login: User AD login.
        :param ad_domain: User AD domain.

        :return: User information.
        """

        method = SearchUserByLoginMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISearchUserByLoginRequestPayload.from_domain(
            ad_login=ad_login,
            ad_domain=ad_domain,
        )

        botx_api_user_from_search = await method.execute(payload)

        return botx_api_user_from_search.to_domain()

    async def search_user_by_other_id(
        self,
        *,
        bot_id: UUID,
        other_id: str,
    ) -> UserFromSearch:
        """Search user by other identificator for search.

        :param bot_id: Bot which should perform the request.
        :param other_id: User other identificator.

        :return: User information.
        """

        method = SearchUserByOtherIdMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISearchUserByOtherIdRequestPayload.from_domain(
            other_id=other_id,
        )

        botx_api_user_from_search = await method.execute(payload)

        return botx_api_user_from_search.to_domain()

    async def update_user_profile(
        self,
        *,
        bot_id: UUID,
        user_huid: UUID,
        avatar: Missing[Union[IncomingFileAttachment, OutgoingAttachment]] = Undefined,
        name: Missing[str] = Undefined,
        public_name: Missing[str] = Undefined,
        company: Missing[str] = Undefined,
        company_position: Missing[str] = Undefined,
        description: Missing[str] = Undefined,
        department: Missing[str] = Undefined,
        office: Missing[str] = Undefined,
        manager: Missing[str] = Undefined,
    ) -> None:
        """Update user profile.

        :param bot_id: Bot which should perform the request.
        :param user_huid: User huid whose profile needs to be updated.
        :param avatar: New user avatar.
        :param name: New user name.
        :param public_name: New user public name.
        :param company: New user company.
        :param company_position: New user company position.
        :param description: New user description.
        :param department: New user department.
        :param office: New user office.
        :param manager: New user manager.
        """
        method = UpdateUsersProfileMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPIUpdateUserProfileRequestPayload.from_domain(
            user_huid=user_huid,
            avatar=avatar,
            name=name,
            public_name=public_name,
            company=company,
            company_position=company_position,
            description=description,
            department=department,
            office=office,
            manager=manager,
        )

        await method.execute(payload)

    # - SmartApps API -
    async def send_smartapp_event(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        data: Dict[str, Any],
        ref: MissingOptional[UUID] = Undefined,
        opts: Missing[Dict[str, Any]] = Undefined,
        files: Missing[List[File]] = Undefined,
    ) -> None:
        """Send SmartApp event.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param data: Event payload.
        :param ref: Request identifier.
        :param opts: Event options.
        :param files: Files.
        """

        method = SmartAppEventMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISmartAppEventRequestPayload.from_domain(
            ref=ref,
            smartapp_id=bot_id,
            chat_id=chat_id,
            data=data,
            opts=opts,
            files=files,
        )

        await method.execute(payload)

    async def send_smartapp_notification(
        self,
        bot_id: UUID,
        chat_id: UUID,
        smartapp_counter: int,
        body: Missing[str] = Undefined,
        opts: Missing[Dict[str, Any]] = Undefined,
        meta: Missing[Dict[str, Any]] = Undefined,
    ) -> None:
        """Send SmartApp notification.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param smartapp_counter: Value app's counter.
        :param body: Event body.
        :param opts: Event options.
        :param meta: Meta information.
        """

        method = SmartAppNotificationMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISmartAppNotificationRequestPayload.from_domain(
            chat_id=chat_id,
            smartapp_counter=smartapp_counter,
            body=body,
            opts=opts,
            meta=meta,
        )

        await method.execute(payload)

    # - Stickers API -
    async def create_sticker_pack(
        self,
        *,
        bot_id: UUID,
        name: str,
        huid: Missing[UUID] = Undefined,
    ) -> StickerPack:
        """Create empty sticker pack.

        :param bot_id: Bot which should perform the request.
        :param name: Sticker pack name.
        :param huid: Sticker pack creator.

        :return: Created sticker pack.
        """

        method = CreateStickerPackMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPICreateStickerPackRequestPayload.from_domain(
            name=name,
            huid=huid,
        )

        botx_api_sticker_pack = await method.execute(payload)

        return botx_api_sticker_pack.to_domain()

    async def add_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        emoji: str,
        async_buffer: AsyncBufferReadable,
    ) -> Sticker:
        """Add sticker in sticker pack.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Sticker pack id to indicate where to add.
        :param emoji: Sticker emoji.
        :param async_buffer: Sticker image file. Only PNG.

        :return: Added sticker.
        """

        await ensure_file_content_is_png(async_buffer)
        await ensure_sticker_image_size_valid(async_buffer)

        method = AddStickerMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = await BotXAPIAddStickerRequestPayload.from_domain(
            sticker_pack_id=sticker_pack_id,
            emoji=emoji,
            async_buffer=async_buffer,
        )

        botx_api_sticker = await method.execute(payload)

        return botx_api_sticker.to_domain(pack_id=sticker_pack_id)

    async def delete_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> None:
        """Delete sticker from sticker pack.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Target sticker pack id.
        :param sticker_id: Sticker id which should be deleted.
        """

        method = DeleteStickerMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = await BotXAPIDeleteStickerRequestPayload.from_domain(
            sticker_id=sticker_id,
            sticker_pack_id=sticker_pack_id,
        )

        await method.execute(payload)

    async def iterate_by_sticker_packs(
        self,
        *,
        bot_id: UUID,
        user_huid: UUID,
    ) -> AsyncIterable[StickerPackFromList]:
        """Iterate by user sticker packs.

        :param bot_id: Bot which should perform the request.
        :param user_huid: User huid.

        :yield: Sticker pack.
        """

        after = None

        method = GetStickerPacksMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        while True:
            payload = BotXAPIGetStickerPacksRequestPayload.from_domain(
                huid=user_huid,
                limit=STICKER_PACKS_PER_PAGE,
                after=after,
            )
            botx_api_sticker_pack_list = await method.execute(payload)

            sticker_pack_page = botx_api_sticker_pack_list.to_domain()
            after = sticker_pack_page.after

            for sticker_pack in sticker_pack_page.sticker_packs:
                yield sticker_pack

            if not after:
                break

    async def get_sticker_pack(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
    ) -> StickerPack:
        """Get sticker pack.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Sticker pack id.

        :return: Sticker pack.
        """

        method = GetStickerPackMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIGetStickerPackRequestPayload.from_domain(
            sticker_pack_id=sticker_pack_id,
        )

        botx_api_sticker_pack = await method.execute(payload)

        return botx_api_sticker_pack.to_domain()

    async def delete_sticker_pack(self, *, bot_id: UUID, sticker_pack_id: UUID) -> None:
        """Delete existing sticker pack.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Target sticker pack.
        """

        method = DeleteStickerPackMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPIDeleteStickerPackRequestPayload.from_domain(
            sticker_pack_id=sticker_pack_id,
        )

        await method.execute(payload)

    async def get_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> Sticker:
        """Get sticker.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Sticker pack id.
        :param sticker_id: Sticker id.

        :return: Sticker.
        """

        method = GetStickerMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIGetStickerRequestPayload.from_domain(
            sticker_pack_id=sticker_pack_id,
            sticker_id=sticker_id,
        )

        botx_api_sticker = await method.execute(payload)

        return botx_api_sticker.to_domain(pack_id=sticker_pack_id)

    async def edit_sticker_pack(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        name: str,
        preview: UUID,
        stickers_order: List[UUID],
    ) -> StickerPack:
        """Edit Sticker pack.

        :param bot_id: Bot which should perform the request.
        :param sticker_pack_id: Sticker pack id.
        :param name: Sticker pack name.
        :param preview: Sticker from the set selected as a preview.
        :param stickers_order: Sticker IDs in order they are displayed.

        :return: Edited sticker pack.
        """

        method = EditStickerPackMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIEditStickerPackRequestPayload.from_domain(
            sticker_pack_id=sticker_pack_id,
            name=name,
            preview=preview,
            stickers_order=stickers_order,
        )

        botx_api_sticker_pack = await method.execute(payload)

        return botx_api_sticker_pack.to_domain()

    # - Files API -
    async def download_file(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        file_id: UUID,
        async_buffer: AsyncBufferWritable,
    ) -> None:
        """Download file form file service.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param file_id: Async file id.
        :param async_buffer: Buffer to write downloaded file.
        """

        method = DownloadFileMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIDownloadFileRequestPayload.from_domain(
            chat_id=chat_id,
            file_id=file_id,
        )

        await method.execute(payload, async_buffer)

    async def upload_file(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        async_buffer: AsyncBufferReadable,
        filename: str,
        duration: Missing[int] = Undefined,
        caption: Missing[str] = Undefined,
    ) -> File:
        """Upload file to file service.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param async_buffer: Buffer to write downloaded file.
        :param filename: File name.
        :param duration: Video duration.
        :param caption: Text under file.

        :return: Meta info of uploaded file.
        """

        method = UploadFileMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIUploadFileRequestPayload.from_domain(
            chat_id=chat_id,
            duration=duration,
            caption=caption,
        )

        botx_api_async_file = await method.execute(payload, async_buffer, filename)

        return botx_api_async_file.to_domain()

    @staticmethod
    def _build_main_collector(
        collectors: Sequence[HandlerCollector],
        middlewares: List[Middleware],
        exception_handlers: Optional[ExceptionHandlersDict] = None,
    ) -> HandlerCollector:
        main_collector = HandlerCollector(middlewares=middlewares)
        main_collector.insert_exception_middleware(exception_handlers)
        main_collector.include(*collectors)

        return main_collector
