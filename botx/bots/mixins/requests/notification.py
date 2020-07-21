"""Mixin for shortcut for notification resource requests."""

from typing import Optional, Sequence
from uuid import UUID

from botx import converters
from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v3.notification.direct_notification import NotificationDirect
from botx.clients.methods.v3.notification.notification import Notification
from botx.clients.types.message_payload import ResultPayload
from botx.clients.types.options import ResultOptions
from botx.models.messages.sending.credentials import SendingCredentials
from botx.models.messages.sending.payload import MessagePayload


class NotificationRequestsMixin:
    """Mixin for shortcut for notification resource requests."""

    async def send_notification(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        payload: MessagePayload,
        group_chat_ids: Optional[Sequence[UUID]] = None,
    ) -> None:
        """Send notifications into chat.

        Arguments:
            credentials: credentials for making request.
            payload: payload for notification.
            group_chat_ids: IDS of chats into which message should be sent.
        """
        if group_chat_ids is not None:
            chat_ids = converters.optional_sequence_to_list(group_chat_ids)
        elif credentials.chat_id:
            chat_ids = [credentials.chat_id]
        else:
            chat_ids = []

        await self.call_method(
            Notification(
                group_chat_ids=chat_ids,
                result=ResultPayload(
                    body=payload.text,
                    metadata=payload.metadata,
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
        credentials: SendingCredentials,
        payload: MessagePayload,
    ) -> UUID:
        """Send notification into chat.

        Arguments:
            credentials: credentials for making request.
            payload: payload for notification.

        Returns:
            ID sent message.

        Raises:
            ValueError: raised if chat_id wasn't provided
        """
        if not credentials.chat_id:
            raise ValueError("chat_id is required to send direct notification")

        return await self.call_method(
            NotificationDirect(
                group_chat_id=credentials.chat_id,
                event_sync_id=credentials.message_id,
                result=ResultPayload(
                    body=payload.text,
                    metadata=payload.metadata,
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
