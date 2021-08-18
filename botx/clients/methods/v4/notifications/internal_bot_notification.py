"""Method for sending internal bot notification."""
from typing import Any, Dict, List, Optional
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.extractors import extract_generated_sync_id
from botx.clients.types.message_payload import InternalBotNotificationPayload
from botx.clients.types.response_results import InternalBotNotificationResult


class InternalBotNotification(AuthorizedBotXMethod[UUID]):
    """Method for sending internal bot notification."""

    __url__ = "/api/v4/botx/notifications/internal"
    __method__ = "POST"
    __returning__ = InternalBotNotificationResult
    __result_extractor__ = extract_generated_sync_id

    #: IDs of chats for new notification.
    group_chat_id: UUID

    #: HUIDs of bots that should receive notifications (None for all bots in chat).
    recipients: Optional[List[UUID]] = None

    # notification payload
    data: InternalBotNotificationPayload  # noqa: WPS110

    #: extra options for message.
    opts: Dict[str, Any] = {}
