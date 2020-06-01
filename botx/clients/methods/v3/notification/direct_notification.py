"""Method for sending notification into single chat."""
from typing import Optional
from uuid import UUID

from pydantic import Field

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.methods.extractors import extract_generated_sync_id
from botx.clients.types.message_payload import ResultPayload
from botx.clients.types.options import ResultOptions
from botx.clients.types.response_results import PushResult
from botx.models.files import File
from botx.models.typing import AvailableRecipients


class NotificationDirect(AuthorizedBotXMethod[UUID]):
    """Method for sending notification into single chat."""

    __url__ = "/api/v3/botx/notification/callback/direct"
    __method__ = "POST"
    __returning__ = PushResult
    __result_extractor__ = extract_generated_sync_id

    #: ID of chat for new notification.
    group_chat_id: UUID

    #: custom ID for message.
    event_sync_id: Optional[UUID] = None

    #: HUIDs of users that should receive notifications.
    recipients: AvailableRecipients = "all"

    #: data for build message: body, markup, mentions.
    result: ResultPayload = Field(..., alias="notification")

    #: attached file for message.
    file: Optional[File] = None

    #: extra options for message.
    opts: ResultOptions = ResultOptions()
