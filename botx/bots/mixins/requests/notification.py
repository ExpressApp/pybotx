"""Definition for mixin that defines BotX API methods."""

from typing import Optional, Sequence, cast
from uuid import UUID

from botx import converters
from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.methods.v3.notification.notification import Notification
from botx.clients.types.options import ResultOptions
from botx.clients.types.result_payload import ResultPayload
from botx.models import sending


class NotificationRequestsMixin:
    """Mixin that defines methods for communicating with BotX API."""

    async def send_notification(
        self: BotXMethodCallProtocol,
        credentials: sending.SendingCredentials,
        payload: sending.MessagePayload,
        group_chat_ids: Optional[Sequence[UUID]] = None,
    ) -> None:
        if group_chat_ids is not None:
            chat_ids = converters.optional_sequence_to_list(group_chat_ids)
        else:
            chat_ids = [cast(UUID, credentials.chat_id)]

        return await self.call_method(
            Notification(
                bot_id=cast(UUID, credentials.bot_id),
                group_chat_ids=chat_ids,
                result=ResultPayload(
                    body=payload.text,
                    bubble=payload.markup.bubbles,
                    keyboard=payload.markup.keyboard,
                    mentions=payload.options.mentions,
                ),
                recipients=payload.options.recipients,
                file=payload.file,
                opts=ResultOptions(notification_opts=payload.options.notifications),
            ),
            credentials=credentials,
        )

    async def send_direct_notification(
        self: BotXMethodCallProtocol,
        credentials: sending.SendingCredentials,
        payload: sending.MessagePayload,
    ) -> UUID:
        return await self.call_method(
            NotificationDirect(
                bot_id=cast(UUID, credentials.bot_id),
                group_chat_id=cast(UUID, credentials.chat_id),
                event_sync_id=credentials.message_id,
                result=ResultPayload(
                    body=payload.text,
                    bubble=payload.markup.bubbles,
                    keyboard=payload.markup.keyboard,
                    mentions=payload.options.mentions,
                ),
                recipients=payload.options.recipients,
                file=payload.file,
                opts=ResultOptions(notification_opts=payload.options.notifications),
            ),
            credentials=credentials,
        )
