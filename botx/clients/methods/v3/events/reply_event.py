"""Method for sending command result into chat."""

from typing import Optional
from uuid import UUID

from pydantic import Field

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.types.message_payload import ResultPayload
from botx.clients.types.options import ResultOptions
from botx.models.files import File


class ReplyEvent(AuthorizedBotXMethod[UUID]):
    """Method for sending reply message."""

    __url__ = "/api/v3/botx/events/reply_event"
    __method__ = "POST"
    __returning__ = str

    #: ID of message for reply.
    source_sync_id: Optional[UUID] = None

    #: message payload.
    result: ResultPayload = Field(..., alias="reply")

    #: attached file.
    file: Optional[File] = None

    #: extra options for new message.
    opts: ResultOptions = ResultOptions()
