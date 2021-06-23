"""Method for sending smartapp event."""
from typing import Any, List, Optional
from uuid import UUID

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.models.files import File


class SmartAppEvent(AuthorizedBotXMethod[str]):
    """Method for editing sent event."""

    __url__ = "/api/v3/botx/smartapps/event"
    __method__ = "POST"
    __returning__ = str
    #: uniq id of request
    ref: Optional[UUID] = None

    #:id of smartapp
    smartapp_id: UUID

    #: user's data
    data: Any

    #: options of smartapp
    opts: Any

    #: version of protocol smartapp <-> bot
    smartapp_api_version: int

    #: chat of this smartapp (smartapp_id now)
    group_chat_id: UUID

    #: files
    files: List[File]


class SmartAppNotification(AuthorizedBotXMethod[str]):
    """Method for editing sent event."""

    __url__ = "/api/v3/botx/smartapps/notification"
    __method__ = "POST"
    __returning__ = str
    #: chat of this smartapp
    group_chat_id: UUID

    #: unread notifications count
    smartapp_counter: int

    #: options of smartapp
    opts: Any

    #: version of protocol smartapp <-> bot
    smartapp_api_version: int
