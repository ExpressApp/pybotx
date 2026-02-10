from __future__ import annotations

from typing import Any
from uuid import UUID

from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.attachments import IncomingFileAttachment, OutgoingAttachment
from pybotx.domain.models.message.markup import BubbleMarkup, KeyboardMarkup
from pybotx.domain.models.message.message_status import MessageStatus
from pybotx.infrastructure.client.events_api.delete_event import (
    BotXAPIDeleteEventRequestPayload,
    DeleteEventMethod,
)
from pybotx.infrastructure.client.events_api.edit_event import (
    BotXAPIEditEventRequestPayload,
    EditEventMethod,
)
from pybotx.infrastructure.client.events_api.message_status_event import (
    BotXAPIMessageStatusRequestPayload,
    MessageStatusMethod,
)
from pybotx.infrastructure.client.events_api.reply_event import (
    BotXAPIReplyEventRequestPayload,
    ReplyEventMethod,
)
from pybotx.infrastructure.client.events_api.stop_typing_event import (
    BotXAPIStopTypingEventRequestPayload,
    StopTypingEventMethod,
)
from pybotx.infrastructure.client.events_api.typing_event import (
    BotXAPITypingEventRequestPayload,
    TypingEventMethod,
)
from pybotx.domain.ports.botx_api import MissingOptionalAttachment


class EventsApiMixin:
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
    ) -> None:
        method = self._method_factory.build(EditEventMethod, bot_id=bot_id)
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
    ) -> None:
        method = self._method_factory.build(ReplyEventMethod, bot_id=bot_id)
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

        await method.execute(payload)

    async def get_message_status(self, *, bot_id: UUID, sync_id: UUID) -> MessageStatus:
        method = self._method_factory.build(MessageStatusMethod, bot_id=bot_id)
        payload = BotXAPIMessageStatusRequestPayload.from_domain(sync_id=sync_id)
        botx_api_message_status = await method.execute(payload)
        return botx_api_message_status.to_domain()

    async def start_typing(self, *, bot_id: UUID, chat_id: UUID) -> None:
        method = self._method_factory.build(TypingEventMethod, bot_id=bot_id)
        payload = BotXAPITypingEventRequestPayload.from_domain(chat_id=chat_id)
        await method.execute(payload)

    async def stop_typing(self, *, bot_id: UUID, chat_id: UUID) -> None:
        method = self._method_factory.build(StopTypingEventMethod, bot_id=bot_id)
        payload = BotXAPIStopTypingEventRequestPayload.from_domain(chat_id=chat_id)
        await method.execute(payload)

    async def delete_message(self, *, bot_id: UUID, sync_id: UUID) -> None:
        method = self._method_factory.build(DeleteEventMethod, bot_id=bot_id)
        payload = BotXAPIDeleteEventRequestPayload.from_domain(sync_id=sync_id)
        await method.execute(payload)
