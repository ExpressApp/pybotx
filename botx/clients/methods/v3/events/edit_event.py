from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from botx.clients.methods.base import AuthorizedBotXMethod
from botx.clients.types.options import ResultOptions
from botx.models.constants import MAXIMUM_TEXT_LENGTH
from botx.models.enums import Statuses
from botx.models.mentions import Mention
from botx.models.typing import BubbleMarkup, KeyboardMarkup


class UpdatePayload(BaseModel):
    """Data that is sent when bot updates message."""

    status: Statuses = Field(Statuses.ok, const=True)
    """status of operation. *Not used for now*."""
    body: Optional[str] = Field(None, max_length=MAXIMUM_TEXT_LENGTH)
    """new body in message."""
    keyboard: Optional[KeyboardMarkup] = None
    """new keyboard that will be used for new message."""
    bubble: Optional[BubbleMarkup] = None
    """new bubble elements that will be showed under new message."""
    mentions: Optional[List[Mention]] = None
    """new mentions that BotX API will append before new message text."""


class EditEvent(AuthorizedBotXMethod[str]):
    __url__ = "/api/v3/botx/events/edit_event"
    __method__ = "POST"
    __returning__ = str

    sync_id: UUID
    result: UpdatePayload = Field(..., alias="payload")
    opts: ResultOptions = ResultOptions()
