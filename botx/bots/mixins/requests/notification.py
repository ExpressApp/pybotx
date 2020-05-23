"""Definition for mixin that defines BotX API methods."""

from typing import TYPE_CHECKING, Optional, Sequence, cast
from uuid import UUID

from botx import utils
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.methods.v3.notification.notification import Notification
from botx.clients.types.options import ResultOptions
from botx.clients.types.result_payload import ResultPayload
from botx.models import sending

if TYPE_CHECKING:
    from botx.bots.bot import Bot  # noqa: WPS433


class NotificationRequestsMixin:
    """Mixin that defines methods for communicating with BotX API."""

    async def send_notification(
        self: "Bot",
        credentials: sending.SendingCredentials,
        payload: sending.MessagePayload,
        group_chat_ids: Optional[Sequence[UUID]] = None,
    ) -> None:
        if group_chat_ids is not None:
            chat_ids = utils.optional_sequence_to_list(group_chat_ids)
        else:
            chat_ids = [credentials.chat_id]

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
        self: "Bot",
        credentials: sending.SendingCredentials,
        payload: sending.MessagePayload,
    ) -> UUID:
        return await self.call_method(
            NotificationDirect(
                bot_id=cast(UUID, credentials.bot_id),
                group_chat_id=credentials.chat_id,
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
