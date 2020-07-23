"""Method for editing sent event."""
from uuid import UUID

from pydantic import Field

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.types.message_payload import UpdatePayload
from botx.clients.types.options import ResultOptions


class EditEvent(AuthorizedBotXMethod[str]):
    """Method for editing sent event."""

    __url__ = "/api/v3/botx/events/edit_event"
    __method__ = "POST"
    __returning__ = str

    #: ID of event that should be edited.
    sync_id: UUID

    #: data for editing.
    result: UpdatePayload = Field(..., alias="payload")

    #: extra options for message.
    opts: ResultOptions = ResultOptions()
