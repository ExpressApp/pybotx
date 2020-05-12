from uuid import UUID

from pydantic import Field

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.models.requests import ResultOptions, UpdatePayload


class EditEvent(AuthorizedBotXMethod[str]):
    __url__ = "/api/v3/botx/events/edit_event"
    __method__ = "POST"
    __returning__ = str

    sync_id: UUID
    result: UpdatePayload = Field(..., alias="payload")
    opts: ResultOptions = ResultOptions()
