from typing import List

from pydantic import BaseModel, Field

from botx.models.constants import MAXIMUM_TEXT_LENGTH
from botx.models.enums import Statuses
from botx.models.mentions import Mention
from botx.models.typing import BubbleMarkup, KeyboardMarkup


class ResultPayload(BaseModel):
    """Data that is sent when bot answers on command or send notification."""

    status: Statuses = Field(Statuses.ok, const=True)
    """status of operation. *Not used for now*."""
    body: str = Field("", max_length=MAXIMUM_TEXT_LENGTH)
    """body for new message from bot."""
    keyboard: KeyboardMarkup = []
    """keyboard that will be used for new message."""
    bubble: BubbleMarkup = []
    """bubble elements that will be showed under new message."""
    mentions: List[Mention] = []
    """mentions that BotX API will append before new message text."""
