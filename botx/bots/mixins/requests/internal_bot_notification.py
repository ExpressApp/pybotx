"""Mixin for shortcut for internal bot notification resource requests."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from botx.bots.mixins.requests.call_protocol import BotXMethodCallProtocol
from botx.clients.methods.v4.bots.internal_bot_notification import (
    InternalBotNotification,
)
from botx.clients.types.message_payload import InternalBotNotificationPayload
from botx.models.messages.sending.credentials import SendingCredentials


class InternalBotNotificationRequestsMixin:
    """Mixin for shortcut for internal bot notification resource requests."""

    async def internal_bot_notification(
        self: BotXMethodCallProtocol,
        credentials: SendingCredentials,
        group_chat_id: UUID,
        text: str,
        sender: str = None,
        recipients: Optional[List[UUID]] = None,
        opts: Optional[Dict[str, Any]] = None,
    ) -> UUID:
        """Send internal bot notifications into chat.

        Arguments:
            credentials: credentials for making request.
            text: notification text.
            sender: information about notification sender.
            group_chat_id: ID of chats into which message should be sent.
        """

        return await self.call_method(
            InternalBotNotification(
                group_chat_id=group_chat_id,
                recipients=recipients,
                data=InternalBotNotificationPayload(message=text, sender=sender),
                opts=opts or {},
            ),
            credentials=credentials,
        )
