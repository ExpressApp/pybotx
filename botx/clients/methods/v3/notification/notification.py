"""Method for sending notification into many chats."""
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.types.message_payload import ResultPayload
from botx.clients.types.options import ResultOptions
from botx.models.files import File
from botx.models.typing import AvailableRecipients


class Notification(AuthorizedBotXMethod[str]):
    """Method for sending notification into many chats."""

    __url__ = "/api/v3/botx/notification/callback"
    __method__ = "POST"
    __returning__ = str

    #: IDs of chats for new notification.
    group_chat_ids: List[UUID] = []

    #: HUIDs of users that should receive notifications.
    recipients: AvailableRecipients = "all"

    #: data for build message: body, markup, mentions.
    result: ResultPayload = Field(..., alias="notification")

    #: attached file for message.
    file: Optional[File] = None

    #: extra options for message.
    opts: ResultOptions = ResultOptions()
