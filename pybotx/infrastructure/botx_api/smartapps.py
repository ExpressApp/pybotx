from __future__ import annotations

from typing import Any
from uuid import UUID

from pybotx.domain.missing import Missing, MissingOptional, Undefined
from pybotx.domain.models.async_files import File
from pybotx.domain.ports.async_buffer import AsyncBufferReadable
from pybotx.domain.models.smartapps import SmartApp
from pybotx.domain.models.smartapp_manifest import (
    SmartappManifest,
    SmartappManifestAndroidParams,
    SmartappManifestIosParams,
    SmartappManifestUnreadCounterParams,
    SmartappManifestWebParams,
)
from pybotx.infrastructure.client.smartapps_api.smartapp_custom_notification import (
    BotXAPISmartAppCustomNotificationRequestPayload,
    SmartAppCustomNotificationMethod,
)
from pybotx.infrastructure.client.smartapps_api.smartapp_event import (
    BotXAPISmartAppEventRequestPayload,
    SmartAppEventMethod,
)
from pybotx.infrastructure.client.smartapps_api.smartapp_manifest import (
    BotXAPISmartAppManifestRequestPayload,
    SmartAppManifestMethod,
)
from pybotx.infrastructure.client.smartapps_api.smartapp_notification import (
    BotXAPISmartAppNotificationRequestPayload,
    SmartAppNotificationMethod,
)
from pybotx.infrastructure.client.smartapps_api.smartapp_unread_counter import (
    BotXAPISmartAppUnreadCounterRequestPayload,
    SmartAppUnreadCounterMethod,
)
from pybotx.infrastructure.client.smartapps_api.smartapps_list import (
    BotXAPISmartAppsListRequestPayload,
    SmartAppsListMethod,
)
from pybotx.infrastructure.client.smartapps_api.upload_file import (
    UploadFileMethod as SmartappsUploadFileMethod,
)


class SmartAppsApiMixin:
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
        method = self._method_factory.build(SmartAppEventMethod, bot_id=bot_id)
        payload = BotXAPISmartAppEventRequestPayload.from_domain(
            chat_id=chat_id,
            smartapp_id=bot_id,
            data=data,
            encrypted=encrypted,
            ref=ref,
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
        opts: Missing[dict[str, Any]] = Undefined,
        meta: Missing[dict[str, Any]] = Undefined,
    ) -> None:
        method = self._method_factory.build(SmartAppNotificationMethod, bot_id=bot_id)
        payload = BotXAPISmartAppNotificationRequestPayload.from_domain(
            chat_id=chat_id,
            smartapp_counter=smartapp_counter,
            body=body,
            opts=opts,
            meta=meta,
        )
        await method.execute(payload)

    async def get_smartapps_list(
        self,
        *,
        bot_id: UUID,
        version: Missing[int] = Undefined,
    ) -> tuple[list[SmartApp], int]:
        method = self._method_factory.build(SmartAppsListMethod, bot_id=bot_id)
        payload = BotXAPISmartAppsListRequestPayload.from_domain(version=version)
        botx_api_smartapps_list = await method.execute(payload)
        return botx_api_smartapps_list.to_domain()

    async def send_smartapp_manifest(
        self,
        *,
        bot_id: UUID,
        ios: Missing[SmartappManifestIosParams] = Undefined,
        android: Missing[SmartappManifestAndroidParams] = Undefined,
        web_layout: Missing[SmartappManifestWebParams] = Undefined,
        unread_counter: Missing[SmartappManifestUnreadCounterParams] = Undefined,
    ) -> SmartappManifest:
        method = self._method_factory.build(SmartAppManifestMethod, bot_id=bot_id)
        payload = BotXAPISmartAppManifestRequestPayload.from_domain(
            ios=ios,
            android=android,
            web_layout=web_layout,
            unread_counter=unread_counter,
        )
        botx_api_smartapp_manifest = await method.execute(payload)
        return botx_api_smartapp_manifest.to_domain()

    async def upload_static_file(
        self,
        *,
        bot_id: UUID,
        async_buffer: AsyncBufferReadable,
        filename: str,
    ) -> str:
        method = self._method_factory.build(SmartappsUploadFileMethod, bot_id=bot_id)
        botx_api_static_file = await method.execute(async_buffer, filename)
        return botx_api_static_file.to_domain()

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
        method = self._method_factory.build(
            SmartAppCustomNotificationMethod,
            bot_id=bot_id,
            with_callbacks=True,
        )
        payload = BotXAPISmartAppCustomNotificationRequestPayload.from_domain(
            group_chat_id=group_chat_id,
            title=title,
            body=body,
            meta=meta,
        )
        botx_api_sync_id = await method.execute(
            payload,
            wait_callback,
            callback_timeout,
            self._default_callback_timeout,
        )
        return botx_api_sync_id.to_domain()

    async def send_smartapp_unread_counter(
        self,
        *,
        bot_id: UUID,
        group_chat_id: UUID,
        counter: int,
        wait_callback: bool = True,
        callback_timeout: float | None = None,
    ) -> UUID:
        method = self._method_factory.build(
            SmartAppUnreadCounterMethod,
            bot_id=bot_id,
            with_callbacks=True,
        )
        payload = BotXAPISmartAppUnreadCounterRequestPayload.from_domain(
            group_chat_id=group_chat_id,
            counter=counter,
        )
        botx_api_sync_id = await method.execute(
            payload,
            wait_callback,
            callback_timeout,
            self._default_callback_timeout,
        )
        return botx_api_sync_id.to_domain()
