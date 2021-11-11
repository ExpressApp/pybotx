"""Method for sending smartapp event."""
from typing import Any, Dict, Optional
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod


class SmartAppNotification(AuthorizedBotXMethod[str]):
    """Method for sending smartapp notifications."""

    __url__ = "/api/v3/botx/smartapps/notification"
    __method__ = "POST"
    __returning__ = str

    #: smartapp chat
    group_chat_id: Optional[UUID]

    #: unread notifications count
    smartapp_counter: int

    #: event options
    opts: Dict[str, Any] = {}

    #: version of protocol smartapp <-> bot
    smartapp_api_version: int
