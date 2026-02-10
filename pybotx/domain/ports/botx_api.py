from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any, AsyncContextManager, Protocol, runtime_checkable
from uuid import UUID

from pybotx.domain.missing import Missing, MissingOptional, Undefined
from pybotx.domain.ports.async_buffer import AsyncBufferReadable, AsyncBufferWritable
from pybotx.domain.ports.http_client import HttpClientPort
from pybotx.domain.models.async_files import File
from pybotx.domain.models.bot_catalog import BotsListItem
from pybotx.domain.models.chats import ChatInfo, ChatLink, ChatListItem
from pybotx.domain.models.enums import ChatLinkTypes, ChatTypes
from pybotx.domain.models.message.markup import BubbleMarkup, KeyboardMarkup
from pybotx.domain.models.message.message_status import MessageStatus
from pybotx.domain.models.stickers import Sticker, StickerPack, StickerPackFromList, StickerPackPage
from pybotx.domain.models.smartapps import SmartApp
from pybotx.domain.models.smartapp_manifest import (
    SmartappManifest,
    SmartappManifestAndroidParams,
    SmartappManifestIosParams,
    SmartappManifestUnreadCounterParams,
    SmartappManifestWebParams,
)
from pybotx.domain.models.users import UserFromCSV, UserFromSearch
from pybotx.domain.models.attachments import IncomingFileAttachment, OutgoingAttachment

MissingOptionalAttachment = MissingOptional[IncomingFileAttachment | OutgoingAttachment]


@runtime_checkable
class BotXApiPort(Protocol):
    async def aclose(self) -> None: ...  # pragma: no cover

    def get_http_client(self) -> HttpClientPort: ...  # pragma: no cover

    def get_default_callback_timeout(self) -> float: ...  # pragma: no cover

    async def get_token(self, *, bot_id: UUID) -> str: ...  # pragma: no cover

    async def get_bots_list(
        self,
        *,
        bot_id: UUID,
        since: Missing[datetime] = Undefined,
    ) -> tuple[list[BotsListItem], datetime]: ...  # pragma: no cover

    async def send_message(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        body: str,
        metadata: Missing[dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        recipients: Missing[list[UUID]] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID: ...  # pragma: no cover

    async def send_message_sync(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        body: str,
        metadata: Missing[dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        recipients: Missing[list[UUID]] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
    ) -> UUID: ...  # pragma: no cover

    async def send_internal_bot_notification(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        data: dict[str, Any],
        opts: Missing[dict[str, Any]] = Undefined,
        recipients: Missing[list[UUID]] = Undefined,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID: ...  # pragma: no cover

    async def edit_message(
        self,
        *,
        bot_id: UUID,
        sync_id: UUID,
        body: Missing[str] = Undefined,
        metadata: Missing[dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: MissingOptionalAttachment = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
    ) -> None: ...  # pragma: no cover

    async def reply_message(
        self,
        *,
        bot_id: UUID,
        sync_id: UUID,
        body: str,
        metadata: Missing[dict[str, Any]] = Undefined,
        bubbles: Missing[BubbleMarkup] = Undefined,
        keyboard: Missing[KeyboardMarkup] = Undefined,
        file: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined,
        silent_response: Missing[bool] = Undefined,
        markup_auto_adjust: Missing[bool] = Undefined,
        stealth_mode: Missing[bool] = Undefined,
        send_push: Missing[bool] = Undefined,
        ignore_mute: Missing[bool] = Undefined,
    ) -> None: ...  # pragma: no cover

    async def get_message_status(
        self,
        *,
        bot_id: UUID,
        sync_id: UUID,
    ) -> MessageStatus: ...  # pragma: no cover

    async def start_typing(self, *, bot_id: UUID, chat_id: UUID) -> None: ...  # pragma: no cover

    async def stop_typing(self, *, bot_id: UUID, chat_id: UUID) -> None: ...  # pragma: no cover

    async def delete_message(self, *, bot_id: UUID, sync_id: UUID) -> None: ...  # pragma: no cover

    async def list_chats(self, *, bot_id: UUID) -> list[ChatListItem]: ...  # pragma: no cover

    async def chat_info(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> ChatInfo: ...  # pragma: no cover

    async def personal_chat(self, *, bot_id: UUID, user_huid: UUID) -> ChatInfo: ...  # pragma: no cover

    async def add_users_to_chat(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: list[UUID],
    ) -> None: ...  # pragma: no cover

    async def remove_users_from_chat(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: list[UUID],
    ) -> None: ...  # pragma: no cover

    async def promote_to_chat_admins(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        huids: list[UUID],
    ) -> None: ...  # pragma: no cover

    async def enable_stealth(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        disable_web_client: Missing[bool] = Undefined,
        ttl_after_read: Missing[int] = Undefined,
        total_ttl: Missing[int] = Undefined,
    ) -> None: ...  # pragma: no cover

    async def disable_stealth(self, *, bot_id: UUID, chat_id: UUID) -> None: ...  # pragma: no cover

    async def create_chat(
        self,
        *,
        bot_id: UUID,
        name: str,
        chat_type: ChatTypes,
        huids: list[UUID],
        description: str | None = None,
        shared_history: Missing[bool] = Undefined,
        avatar: str | None = None,
    ) -> UUID: ...  # pragma: no cover

    async def create_chat_link(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        link_type: ChatLinkTypes,
        access_code: Missing[str | None] = Undefined,
        link_ttl: Missing[int | None] = Undefined,
    ) -> ChatLink: ...  # pragma: no cover

    async def create_thread(self, bot_id: UUID, sync_id: UUID) -> UUID: ...  # pragma: no cover

    async def pin_message(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        sync_id: UUID,
    ) -> None: ...  # pragma: no cover

    async def unpin_message(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
    ) -> None: ...  # pragma: no cover

    async def search_user_by_emails(
        self,
        *,
        bot_id: UUID,
        emails: list[str],
    ) -> list[UserFromSearch]: ...  # pragma: no cover

    async def search_user_by_email_post(
        self,
        *,
        bot_id: UUID,
        email: str,
    ) -> UserFromSearch: ...  # pragma: no cover

    async def search_user_by_email(
        self,
        *,
        bot_id: UUID,
        email: str,
    ) -> UserFromSearch: ...  # pragma: no cover

    async def search_user_by_huid(
        self,
        *,
        bot_id: UUID,
        huid: UUID,
    ) -> UserFromSearch: ...  # pragma: no cover

    async def search_user_by_ad(
        self,
        *,
        bot_id: UUID,
        ad_login: str,
        ad_domain: str,
    ) -> UserFromSearch: ...  # pragma: no cover

    async def search_user_by_other_id(
        self,
        *,
        bot_id: UUID,
        other_id: str,
    ) -> UserFromSearch: ...  # pragma: no cover

    async def update_user_profile(
        self,
        *,
        bot_id: UUID,
        user_huid: UUID,
        avatar: Missing[IncomingFileAttachment | OutgoingAttachment] = Undefined,
        name: Missing[str] = Undefined,
        public_name: Missing[str] = Undefined,
        company: Missing[str] = Undefined,
        company_position: Missing[str] = Undefined,
        description: Missing[str] = Undefined,
        department: Missing[str] = Undefined,
        office: Missing[str] = Undefined,
        manager: Missing[str] = Undefined,
    ) -> None: ...  # pragma: no cover

    def users_as_csv(
        self,
        *,
        bot_id: UUID,
        cts_user: bool = True,
        unregistered: bool = True,
        botx: bool = False,
    ) -> AsyncContextManager[AsyncIterator[UserFromCSV]]: ...  # pragma: no cover

    async def send_smartapp_event(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        data: dict[str, Any],
        encrypted: bool = True,
        ref: MissingOptional[UUID] = Undefined,
        opts: Missing[dict[str, Any]] = Undefined,
        files: Missing[list[File]] = Undefined,
    ) -> None: ...  # pragma: no cover

    async def send_smartapp_notification(
        self,
        bot_id: UUID,
        chat_id: UUID,
        smartapp_counter: int,
        body: Missing[str] = Undefined,
        opts: Missing[dict[str, Any]] = Undefined,
        meta: Missing[dict[str, Any]] = Undefined,
    ) -> None: ...  # pragma: no cover

    async def get_smartapps_list(
        self,
        *,
        bot_id: UUID,
        version: Missing[int] = Undefined,
    ) -> tuple[list[SmartApp], int]: ...  # pragma: no cover

    async def send_smartapp_manifest(
        self,
        *,
        bot_id: UUID,
        ios: Missing[SmartappManifestIosParams] = Undefined,
        android: Missing[SmartappManifestAndroidParams] = Undefined,
        web_layout: Missing[SmartappManifestWebParams] = Undefined,
        unread_counter: Missing[SmartappManifestUnreadCounterParams] = Undefined,
    ) -> SmartappManifest: ...  # pragma: no cover

    async def upload_static_file(
        self,
        *,
        bot_id: UUID,
        async_buffer: AsyncBufferReadable,
        filename: str,
    ) -> str: ...  # pragma: no cover

    async def send_smartapp_custom_notification(
        self,
        *,
        bot_id: UUID,
        group_chat_id: UUID,
        title: str,
        body: str,
        meta: Missing[dict[str, Any]] = Undefined,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID: ...  # pragma: no cover

    async def send_smartapp_unread_counter(
        self,
        *,
        bot_id: UUID,
        group_chat_id: UUID,
        counter: int,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID: ...  # pragma: no cover

    async def create_sticker_pack(
        self,
        *,
        bot_id: UUID,
        name: str,
        huid: Missing[UUID] = Undefined,
    ) -> StickerPack: ...  # pragma: no cover

    async def add_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        emoji: str,
        async_buffer: AsyncBufferReadable,
    ) -> Sticker: ...  # pragma: no cover

    async def delete_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> None: ...  # pragma: no cover

    async def get_sticker_packs(
        self,
        *,
        bot_id: UUID,
        user_huid: UUID,
        limit: int,
        after: str | None = None,
    ) -> StickerPackPage: ...  # pragma: no cover

    async def get_sticker_pack(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
    ) -> StickerPack: ...  # pragma: no cover

    async def delete_sticker_pack(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
    ) -> None: ...  # pragma: no cover

    async def get_sticker(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        sticker_id: UUID,
    ) -> Sticker: ...  # pragma: no cover

    async def edit_sticker_pack(
        self,
        *,
        bot_id: UUID,
        sticker_pack_id: UUID,
        name: str,
        preview: UUID,
        stickers_order: list[UUID],
    ) -> StickerPack: ...  # pragma: no cover

    async def download_file(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        file_id: UUID,
        async_buffer: AsyncBufferWritable,
        is_preview: bool = False,
    ) -> None: ...  # pragma: no cover

    async def upload_file(
        self,
        *,
        bot_id: UUID,
        chat_id: UUID,
        async_buffer: AsyncBufferReadable,
        filename: str,
        duration: Missing[int] = Undefined,
        caption: Missing[str] = Undefined,
    ) -> File: ...  # pragma: no cover

    async def refresh_access_token(
        self,
        *,
        bot_id: UUID,
        huid: UUID,
        ref: UUID | None = None,
    ) -> None: ...  # pragma: no cover

    async def collect_metric(
        self,
        bot_id: UUID,
        bot_function: str,
        huids: list[UUID],
        chat_id: UUID,
    ) -> None: ...  # pragma: no cover

    async def download_url(
        self,
        *,
        url: str,
        async_buffer: AsyncBufferWritable,
    ) -> None: ...  # pragma: no cover
