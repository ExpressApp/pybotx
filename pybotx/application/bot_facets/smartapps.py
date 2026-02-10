from __future__ import annotations

from typing import Any
from uuid import UUID

from pybotx.domain.missing import Missing, MissingOptional, Undefined
from pybotx.domain.models.async_files import File
from pybotx.domain.models.smartapps import SmartApp
from pybotx.domain.models.smartapp_manifest import (
    SmartappManifest,
    SmartappManifestAndroidParams,
    SmartappManifestIosParams,
    SmartappManifestUnreadCounterParams,
    SmartappManifestWebParams,
)
from pybotx.domain.ports.async_buffer import AsyncBufferReadable


class BotSmartAppsMixin:
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
    ) -> None:
        """Send SmartApp event.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param data: Event payload.
        :param ref: Request identifier.
        :param opts: Event options.
        :param files: Files.
        :param encrypted: Encrypt payload.
        """
        await self._botx_api.send_smartapp_event(
            bot_id=bot_id,
            chat_id=chat_id,
            data=data,
            encrypted=encrypted,
            ref=ref,
            opts=opts,
            files=files,
        )

    async def send_smartapp_notification(
        self,
        bot_id: UUID,
        chat_id: UUID,
        smartapp_counter: int,
        body: Missing[str] = Undefined,
        opts: Missing[dict[str, Any]] = Undefined,
        meta: Missing[dict[str, Any]] = Undefined,
    ) -> None:
        """Send SmartApp notification.

        :param bot_id: Bot which should perform the request.
        :param chat_id: Target chat id.
        :param smartapp_counter: Value app's counter.
        :param body: Event body.
        :param opts: Event options.
        :param meta: Meta information.
        """
        await self._botx_api.send_smartapp_notification(
            bot_id=bot_id,
            chat_id=chat_id,
            smartapp_counter=smartapp_counter,
            body=body,
            opts=opts,
            meta=meta,
        )

    async def get_smartapps_list(
        self,
        *,
        bot_id: UUID,
        version: Missing[int] = Undefined,
    ) -> tuple[list[SmartApp], int]:
        """Get list of SmartApps on the current CTS.

        :param bot_id: Bot which should perform the request.
        :param version: Specific list version.

        :return: List of SmartApps, list version.
        """
        return await self._botx_api.get_smartapps_list(
            bot_id=bot_id,
            version=version,
        )

    async def send_smartapp_manifest(
        self,
        *,
        bot_id: UUID,
        ios: Missing[SmartappManifestIosParams] = Undefined,
        android: Missing[SmartappManifestAndroidParams] = Undefined,
        web_layout: Missing[SmartappManifestWebParams] = Undefined,
        unread_counter: Missing[SmartappManifestUnreadCounterParams] = Undefined,
    ) -> SmartappManifest:
        """Send smartapp manifest with given parameters.

        :param bot_id: Bot which should perform the request.
        :param ios: Smartapp layout for ios clients.
        :param android: Smartapp layout for android clients.
        :param web_layout: Smartapp layout for web clients.
        :param unread_counter: Entities that can be subscribed to in the unread counter.

        :return: Smartapp manifest with the set parameters received from BotX.
        """
        return await self._botx_api.send_smartapp_manifest(
            bot_id=bot_id,
            ios=ios,
            android=android,
            web_layout=web_layout,
            unread_counter=unread_counter,
        )

    async def upload_static_file(
        self,
        *,
        bot_id: UUID,
        async_buffer: AsyncBufferReadable,
        filename: str,
    ) -> str:
        """Upload static file to file service.

        :param bot_id: Bot which should perform the request.
        :param async_buffer: Buffer to read uploaded file.
        :param filename: File name.

        :return: file link.
        """
        return await self._botx_api.upload_static_file(
            bot_id=bot_id,
            async_buffer=async_buffer,
            filename=filename,
        )

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
    ) -> UUID:
        """Send SmartApp custom notification.

        :param bot_id: Bot which should perform the request.
        :param group_chat_id: Target chat id.
        :param title: Notification title.
        :param body: Notification body.
        :param meta: Meta information.
        :param wait_callback: Block method call until callback received.
        :param callback_timeout: Callback timeout in seconds (or `None` for
            endless waiting).

        :return: Notification sync_id.
        """
        return await self._botx_api.send_smartapp_custom_notification(
            bot_id=bot_id,
            group_chat_id=group_chat_id,
            title=title,
            body=body,
            meta=meta,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )

    async def send_smartapp_unread_counter(
        self,
        *,
        bot_id: UUID,
        group_chat_id: UUID,
        counter: int,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID:
        """Send SmartApp unread counter.

        :param bot_id: Bot which should perform the request.
        :param group_chat_id: Target chat id.
        :param counter: Counter value.
        :param wait_callback: Block method call until callback received.
        :param callback_timeout: Callback timeout in seconds (or `None` for
            endless waiting).

        :return: Sent message's sync_id.
        """
        return await self._botx_api.send_smartapp_unread_counter(
            bot_id=bot_id,
            group_chat_id=group_chat_id,
            counter=counter,
            wait_callback=wait_callback,
            callback_timeout=callback_timeout,
        )
