from types import SimpleNamespace
from typing import Any, AsyncIterable, Dict, List, Optional, Sequence, Union
from uuid import UUID

import httpx
from pydantic import ValidationError, parse_obj_as

from botx.async_buffer import AsyncBufferReadable, AsyncBufferWritable
from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.bot.callbacks_manager import CallbacksManager
from botx.bot.contextvars import bot_id_var, chat_id_var
from botx.bot.exceptions import AnswerDestinationLookupError
from botx.bot.handler import Middleware
from botx.bot.handler_collector import HandlerCollector
from botx.bot.middlewares.exception_middleware import ExceptionHandlersDict
from botx.client.chats_api.add_admin import (
    AddAdminMethod,
    BotXAPIAddAdminRequestPayload,
)
from botx.client.chats_api.add_user import AddUserMethod, BotXAPIAddUserRequestPayload
from botx.client.chats_api.chat_info import (
    BotXAPIChatInfoRequestPayload,
    ChatInfoMethod,
)
from botx.client.chats_api.create_chat import (
    BotXAPICreateChatRequestPayload,
    CreateChatMethod,
)
from botx.client.chats_api.disable_stealth import (
    BotXAPIDisableStealthRequestPayload,
    DisableStealthMethod,
)
from botx.client.chats_api.list_chats import ListChatsMethod
from botx.client.chats_api.pin_message import (
    BotXAPIPinMessageRequestPayload,
    PinMessageMethod,
)
from botx.client.chats_api.remove_user import (
    BotXAPIRemoveUserRequestPayload,
    RemoveUserMethod,
)
from botx.client.chats_api.set_stealth import (
    BotXAPISetStealthRequestPayload,
    SetStealthMethod,
)
from botx.client.chats_api.unpin_message import (
    BotXAPIUnpinMessageRequestPayload,
    UnpinMessageMethod,
)
from botx.client.events_api.edit_event import (
    BotXAPIEditEventRequestPayload,
    EditEventMethod,
)
from botx.client.events_api.reply_event import (
    BotXAPIReplyEventRequestPayload,
    ReplyEventMethod,
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
from botx.client.notifications_api.direct_notification import (
    BotXAPIDirectNotificationRequestPayload,
    DirectNotificationMethod,
)
from botx.client.notifications_api.internal_bot_notification import (
    BotXAPIInternalBotNotificationRequestPayload,
    InternalBotNotificationMethod,
)
from botx.client.smartapps_api.smartapp_event import (
    BotXAPISmartAppEventRequestPayload,
    SmartAppEventMethod,
)
from botx.client.smartapps_api.smartapp_notification import (
    BotXAPISmartAppNotificationRequestPayload,
    SmartAppNotificationMethod,
)
from botx.client.stickers_api.add_sticker import (
    AddStickerMethod,
    BotXAPIAddStickerRequestPayload,
)
from botx.client.stickers_api.create_sticker_pack import (
    BotXAPICreateStickerPackRequestPayload,
    CreateStickerPackMethod,
)
from botx.client.stickers_api.delete_sticker import (
    BotXAPIDeleteStickerRequestPayload,
    DeleteStickerMethod,
)
from botx.client.stickers_api.get_sticker import (
    BotXAPIGetStickerRequestPayload,
    GetStickerMethod,
)
from botx.client.stickers_api.get_sticker_pack import (
    BotXAPIGetStickerPackRequestPayload,
    GetStickerPackMethod,
)
from botx.client.stickers_api.get_sticker_packs import (
    BotXAPIGetStickerPacksRequestPayload,
    GetStickerPacksMethod,
)
from botx.client.users_api.search_user_by_email import (
    BotXAPISearchUserByEmailRequestPayload,
    SearchUserByEmailMethod,
)
from botx.client.users_api.search_user_by_huid import (
    BotXAPISearchUserByHUIDRequestPayload,
    SearchUserByHUIDMethod,
)
from botx.client.users_api.search_user_by_login import (
    BotXAPISearchUserByLoginRequestPayload,
    SearchUserByLoginMethod,
)
from botx.constants import STICKER_PACKS_PER_PAGE
from botx.converters import optional_sequence_to_list
from botx.image_validators import (
    ensure_file_content_is_png,
    ensure_sticker_image_size_valid,
)
from botx.logger import logger, pformat_jsonable_obj
from botx.missing import Missing, MissingOptional, Undefined, not_undefined
from botx.models.async_files import File
from botx.models.attachments import IncomingFileAttachment, OutgoingAttachment
from botx.models.bot_account import BotAccount
from botx.models.chats import ChatInfo, ChatListItem
from botx.models.commands import BotAPICommand, BotCommand
from botx.models.enums import ChatTypes
from botx.models.message.markup import BubbleMarkup, KeyboardMarkup
from botx.models.message.outgoing_message import OutgoingMessage
from botx.models.method_callbacks import BotXMethodCallback
from botx.models.status import (
    BotAPIStatusRecipient,
    BotMenu,
    StatusRecipient,
    build_bot_status_response,
)
from botx.models.stickers import Sticker, StickerPack, StickerPackFromList
from botx.models.users import UserFromSearch

MissingOptionalAttachment = MissingOptional[
    Union[IncomingFileAttachment, OutgoingAttachment]
]


class Bot:
    def __init__(
        self,
        *,
        collectors: Sequence[HandlerCollector],
        bot_accounts: Sequence[BotAccount],
        middlewares: Optional[Sequence[Middleware]] = None,
        httpx_client: Optional[httpx.AsyncClient] = None,
        exception_handlers: Optional[ExceptionHandlersDict] = None,
        default_callback_timeout: Optional[int] = None,
    ) -> None:
        if not collectors:
            logger.warning("Bot has no connected collectors")
        if not bot_accounts:
            logger.warning("Bot has no bot accounts")

        self.state: SimpleNamespace = SimpleNamespace()

        self.default_callback_timeout = default_callback_timeout

        middlewares = optional_sequence_to_list(middlewares)

        self._handler_collector = self._build_main_collector(
            collectors,
            middlewares,
            exception_handlers,
        )

        self._bot_accounts_storage = BotAccountsStorage(list(bot_accounts))
        self._httpx_client = httpx_client or httpx.AsyncClient()

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

        logger.opt(lazy=True).debug(
            "Got command: {command}",
            command=lambda: pformat_jsonable_obj(raw_bot_command),
        )

        bot_command = bot_api_command.to_domain(raw_bot_command)
        self.async_execute_bot_command(bot_command)

    def async_execute_bot_command(self, bot_command: BotCommand) -> None:
        # raise UnknownBotAccountError if no bot account with this bot_id.
        self._bot_accounts_storage.ensure_bot_id_exists(bot_command.bot.id)

        self._handler_collector.async_handle_bot_command(self, bot_command)

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
        return await self._handler_collector.get_bot_menu(status_recipient, self)

    def set_raw_botx_method_result(
        self,
        raw_botx_method_result: Dict[str, Any],
    ) -> None:
        logger.debug("Got callback: {callback}", callback=raw_botx_method_result)

        callback: BotXMethodCallback = parse_obj_as(
            # Same ignore as in pydantic
            BotXMethodCallback,  # type: ignore[arg-type]
            raw_botx_method_result,
        )

        self._callback_manager.set_botx_method_callback_result(callback)

    async def startup(self) -> None:
        for host, bot_id in self._bot_accounts_storage.iter_host_and_bot_id_pairs():
            try:
                token = await self.get_token(bot_id=bot_id)
            except (InvalidBotAccountError, httpx.HTTPError):
                logger.warning(
                    "Can't get token for bot account: "
                    f"host - {host}, bot_id - {bot_id}",
                )
                continue

            self._bot_accounts_storage.set_token(bot_id, token)

    async def shutdown(self) -> None:
        self._callback_manager.stop_callbacks_waiting()
        await self._handler_collector.wait_active_tasks()
        await self._httpx_client.aclose()

    # - Bots API -
    async def get_token(
        self,
        *,
        bot_id: UUID,
    ) -> str:
        """Get bot auth token.

        Args:
            bot_id: Bot which should perform the request.

        Returns:
            Auth token.
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
        callback_timeout: MissingOptional[int] = Undefined,
    ) -> UUID:
        """Answer to incoming message.

        Works just like `Bot.send`, but `bot_id` and `chat_id` are
        taken from the incoming message.

        Args:
            body: Message body.
            metadata: Notification options.
            bubbles: Bubbles (buttons attached to message) markup.
            keyboard: Keyboard (buttons below message input) markup.
            file: Attachment.
            recipients: List of recipients, empty for all in chat.
            silent_response: (BotX default: False) Exclude next user
                messages from history.
            markup_auto_adjust: (BotX default: False) Move button to next row,
                if its text doesn't fit.
            stealth_mode: (BotX default: False) Enable stealth mode.
            send_push: (BotX default: True) Send push notification on devices.
            ignore_mute: (BotX default: False) Ignore mute or dnd (do not disturb).
            wait_callback: Block method call until callback received.
            callback_timeout: Callback timeout in seconds (or `None` for
                endless waiting).

        Raises:
            AnswerDestinationLookupError: If you try to answer without
                receiving incoming message.

        Returns:
            Notification sync_id.
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
        callback_timeout: MissingOptional[int] = Undefined,
    ) -> UUID:
        """Send internal notification.

        Args:
            message: Built outgoing message.
            wait_callback: Wait for callback.
            callback_timeout: Timeout for waiting for callback.

        Returns:
            Notification sync_id.
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
        callback_timeout: MissingOptional[int] = Undefined,
    ) -> UUID:
        """Send message to chat.

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
            body: Message body.
            metadata: Notification options.
            bubbles: Bubbles (buttons attached to message) markup.
            keyboard: Keyboard (buttons below message input) markup.
            file: Attachment.
            recipients: List of recipients, empty for all in chat.
            silent_response: (BotX default: False) Exclude next user
                messages from history.
            markup_auto_adjust: (BotX default: False) Move button to next row,
                if its text doesn't fit.
            stealth_mode: (BotX default: False) Enable stealth mode.
            send_push: (BotX default: True) Send push notification on devices.
            ignore_mute: (BotX default: False) Ignore mute or dnd (do not disturb).
            wait_callback: Block method call until callback received.
            callback_timeout: Callback timeout in seconds (or `None` for
                endless waiting).

        Returns:
            Notification sync_id.
        """

        method = DirectNotificationMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
            self._callback_manager,
        )

        payload = BotXAPIDirectNotificationRequestPayload.from_domain(
            chat_id,
            body,
            metadata,
            bubbles,
            keyboard,
            file,
            recipients,
            silent_response,
            markup_auto_adjust,
            stealth_mode,
            send_push,
            ignore_mute,
        )
        botx_api_sync_id = await method.execute(
            payload,
            wait_callback,
            not_undefined(callback_timeout, self.default_callback_timeout),
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
        callback_timeout: MissingOptional[int] = Undefined,
    ) -> UUID:
        """Send internal notification.

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
            data: Notification payload.
            opts: Notification options.
            recipients: List of bot uuids, empty for all in chat.
            wait_callback: Wait for callback.
            callback_timeout: Timeout for waiting for callback.

        Returns:
            Notification sync_id.
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
            not_undefined(callback_timeout, self.default_callback_timeout),
        )

        return botx_api_sync_id.to_domain()

    # - Events API -
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
        """Send internal notification.

        Args:
            bot_id: Bot which should perform the request.
            sync_id: `sync_id` of message to update.
            body: New message body. Skip to leave previous body or pass
                empty string to clean it.
            metadata: Notification options. Skip to leave previous metadata.
            bubbles: Bubbles (buttons attached to message) markup. Skip to
                leave previous bubbles.
            keyboard: Keyboard (buttons below message input) markup. Skip
                to leave previous keyboard.
            file: Attachment. Skip to leave previous file or pass `None`
                to clean it.
            markup_auto_adjust: (BotX default: False) Move button to next row,
                if its text doesn't fit.
        """

        method = EditEventMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIEditEventRequestPayload.from_domain(
            sync_id,
            body,
            metadata,
            bubbles,
            keyboard,
            file,
            markup_auto_adjust,
        )

        await method.execute(payload)

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

        Args:
            bot_id: Bot which should perform the request.
            sync_id: `sync_id` of message to reply on.
            body: Reply body.
            metadata: Notification options.
            bubbles: Bubbles (buttons attached to message) markup.
            keyboard: Keyboard (buttons below message input) markup.
            file: Attachment.
            silent_response: (BotX default: False) Exclude next user
                messages from history.
            markup_auto_adjust: (BotX default: False) Move button to next row,
                if its text doesn't fit.
            stealth_mode: (BotX default: False) Enable stealth mode.
            send_push: (BotX default: True) Send push notification on devices.
            ignore_mute: (BotX default: False) Ignore mute or dnd (do not disturb).
        """

        payload = BotXAPIReplyEventRequestPayload.from_domain(
            sync_id,
            body,
            metadata,
            bubbles,
            keyboard,
            file,
            silent_response,
            markup_auto_adjust,
            stealth_mode,
            send_push,
            ignore_mute,
        )
        method = ReplyEventMethod(
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

        Args:
            bot_id: Bot which should perform the request.

        Returns:
            List of chats info.
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

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.

        Returns:
            Chat information.
        """

        method = ChatInfoMethod(bot_id, self._httpx_client, self._bot_accounts_storage)

        payload = BotXAPIChatInfoRequestPayload.from_domain(chat_id)
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

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
            huids: List of eXpress account ids.
        """

        method = AddUserMethod(bot_id, self._httpx_client, self._bot_accounts_storage)

        payload = BotXAPIAddUserRequestPayload.from_domain(chat_id, huids)
        await method.execute(payload)

    async def remove_users_from_chat(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: List[UUID],
    ) -> None:
        """Remove eXpress accounts from chat.

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
            huids: List of eXpress account ids.
        """

        method = RemoveUserMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPIRemoveUserRequestPayload.from_domain(chat_id, huids)
        await method.execute(payload)

    async def promote_to_chat_admins(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: List[UUID],
    ) -> None:
        """Promote users in chat to admins.

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
            huids: List of eXpress account ids.
        """

        method = AddAdminMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPIAddAdminRequestPayload.from_domain(chat_id, huids)
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

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
            disable_web_client: (BotX default: False) Should messages
                be shown in web.
            ttl_after_read: (BotX default: OFF) Time of messages burning after read.
            total_ttl: (BotX default: OFF) Time of messages burning after send.
        """

        method = SetStealthMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISetStealthRequestPayload.from_domain(
            chat_id,
            disable_web_client,
            ttl_after_read,
            total_ttl,
        )

        await method.execute(payload)

    async def disable_stealth(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> None:
        """Disable stealth model. Hides all messages that were in stealth.

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
        """

        method = DisableStealthMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIDisableStealthRequestPayload.from_domain(chat_id)

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

        Args:
            bot_id: Bot which should perform the request.
            name: Chat visible name.
            chat_type: Chat type.
            huids: List of eXpress account ids.
            description: Chat description.
            shared_history: (BotX default: False) Open old chat history for
                new added users.

        Returns:
            Created chat uuid.
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
            shared_history,
            description,
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

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
            sync_id: Target sync id.
        """

        method = PinMessageMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIPinMessageRequestPayload.from_domain(chat_id, sync_id)

        await method.execute(payload)

    async def unpin_message(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> None:
        """Unpin message in chat.

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
        """

        method = UnpinMessageMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIUnpinMessageRequestPayload.from_domain(chat_id)

        await method.execute(payload)

    # - Users API -
    async def search_user_by_email(
        self,
        *,
        bot_id: UUID,
        email: str,
    ) -> UserFromSearch:
        """Search user by email for search.

        Args:
            bot_id: Bot which should perform the request.
            email: User email.

        Returns:
            User information.
        """

        method = SearchUserByEmailMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISearchUserByEmailRequestPayload.from_domain(email)

        botx_api_user_from_search = await method.execute(payload)

        return botx_api_user_from_search.to_domain()

    async def search_user_by_huid(
        self,
        *,
        bot_id: UUID,
        huid: UUID,
    ) -> UserFromSearch:
        """Search user by huid for search.

        Args:
            bot_id: Bot which should perform the request.
            huid: User huid.

        Returns:
            User information.
        """

        method = SearchUserByHUIDMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISearchUserByHUIDRequestPayload.from_domain(huid)

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

        Args:
            bot_id: Bot which should perform the request.
            ad_login: User AD login.
            ad_domain: User AD domain.

        Returns:
            User information.
        """

        method = SearchUserByLoginMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISearchUserByLoginRequestPayload.from_domain(
            ad_login,
            ad_domain,
        )

        botx_api_user_from_search = await method.execute(payload)

        return botx_api_user_from_search.to_domain()

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

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
            data: Event payload.
            ref: Request identifier.
            opts: Event options.
            files: Files.
        """

        method = SmartAppEventMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISmartAppEventRequestPayload.from_domain(
            ref,
            bot_id,
            chat_id,
            data,
            opts,
            files,
        )

        await method.execute(payload)

    async def send_smartapp_notification(
        self,
        bot_id: UUID,
        chat_id: UUID,
        smartapp_counter: int,
        opts: Missing[Dict[str, Any]] = Undefined,
    ) -> None:
        """Send SmartApp notification.

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
            smartapp_counter: Value app's counter.
            opts: Vvent options.
        """

        method = SmartAppNotificationMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPISmartAppNotificationRequestPayload.from_domain(
            chat_id=chat_id,
            smartapp_counter=smartapp_counter,
            opts=opts,
        )

        await method.execute(payload)

    # - Stickers API -
    async def create_sticker_pack(self, *, bot_id: UUID, name: str) -> StickerPack:
        """Create empty sticker pack.

        Args:
            bot_id: Bot which should perform the request.
            name: Sticker pack name.

        Returns:
            Created sticker pack.
        """

        method = CreateStickerPackMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPICreateStickerPackRequestPayload.from_domain(name)

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

        Args:
            bot_id: Bot which should perform the request.
            sticker_pack_id: Sticker pack id to indicate where to add.
            emoji: Sticker emoji.
            async_buffer: Sticker image file. Only PNG.

        Returns:
            Added sticker.
        """

        await ensure_file_content_is_png(async_buffer)
        await ensure_sticker_image_size_valid(async_buffer)

        method = AddStickerMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = await BotXAPIAddStickerRequestPayload.from_domain(
            sticker_pack_id,
            emoji,
            async_buffer,
        )

        botx_api_sticker = await method.execute(payload)

        return botx_api_sticker.to_domain()

    async def delete_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> None:
        """Delete sticker from sticker pack.

        Args:
            bot_id: Bot which should perform the request.
            sticker_pack_id: Target sticker pack id.
            sticker_id: Sticker id which should be deleted.
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

        Args:
            bot_id: Bot which should perform the request.
            user_huid: User huid.

        Yields:
            Sticker pack.
        """

        after = None

        method = GetStickerPacksMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        while True:
            payload = BotXAPIGetStickerPacksRequestPayload.from_domain(
                user_huid,
                STICKER_PACKS_PER_PAGE,
                after,
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

        Args:
            bot_id: Bot which should perform the request.
            sticker_pack_id: Sticker pack id.

        Returns:
            Sticker pack.
        """

        method = GetStickerPackMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIGetStickerPackRequestPayload.from_domain(sticker_pack_id)

        botx_api_sticker_pack = await method.execute(payload)

        return botx_api_sticker_pack.to_domain()

    async def get_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> Sticker:
        """Get sticker.

        Args:
            bot_id: Bot which should perform the request.
            sticker_pack_id: Sticker pack id.
            sticker_id: Sticker id.

        Returns:
            Sticker.
        """

        method = GetStickerMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIGetStickerRequestPayload.from_domain(
            sticker_pack_id,
            sticker_id,
        )

        botx_api_sticker = await method.execute(payload)

        return botx_api_sticker.to_domain()

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

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
            file_id: Async file id.
            async_buffer: Buffer to write downloaded file.
        """

        method = DownloadFileMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIDownloadFileRequestPayload.from_domain(chat_id, file_id)

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

        Args:
            bot_id: Bot which should perform the request.
            chat_id: Target chat id.
            async_buffer: Buffer to write downloaded file.
            filename: File name.
            duration: Video duration.
            caption: Text under file.

        Returns:
            Meta info of uploaded file.
        """

        method = UploadFileMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )
        payload = BotXAPIUploadFileRequestPayload.from_domain(
            chat_id,
            duration,
            caption,
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
