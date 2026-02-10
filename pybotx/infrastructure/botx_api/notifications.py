from __future__ import annotations

from typing import Any
from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.attachments import IncomingFileAttachment, OutgoingAttachment
from pybotx.domain.models.message.markup import BubbleMarkup, KeyboardMarkup
from pybotx.infrastructure.client.notifications_api.direct_notification import (
    BotXAPIDirectNotificationRequestPayload,
    DirectNotificationMethod,
    DirectNotificationSyncMethod,
)
from pybotx.infrastructure.client.notifications_api.internal_bot_notification import (
    BotXAPIInternalBotNotificationRequestPayload,
    InternalBotNotificationMethod,
)


class NotificationsApiMixin:
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
    ) -> UUID:
        method = self._method_factory.build(
            DirectNotificationMethod,
            bot_id=bot_id,
            with_callbacks=True,
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
    ) -> UUID:
        method = self._method_factory.build(DirectNotificationSyncMethod, bot_id=bot_id)

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
        botx_api_sync_id = await method.execute(payload)

        return botx_api_sync_id.to_domain()

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
    ) -> UUID:
        method = self._method_factory.build(
            InternalBotNotificationMethod,
            bot_id=bot_id,
            with_callbacks=True,
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
