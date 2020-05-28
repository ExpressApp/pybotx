"""Shape that is used for new messages from bot."""
from typing import List, Literal

from pydantic import BaseModel, Field

from botx.models.constants import MAXIMUM_TEXT_LENGTH
from botx.models.enums import Statuses
from botx.models.mentions import Mention
from botx.models.typing import BubbleMarkup, KeyboardMarkup


class ResultPayload(BaseModel):
    """Data that is sent when bot answers on command or send notification."""

    #: status of operation.
    status: Literal[Statuses.ok] = Statuses.ok

    #: body for new message from bot.
    body: str = Field("", max_length=MAXIMUM_TEXT_LENGTH)

    #: keyboard that will be used for new message.
    keyboard: KeyboardMarkup = []

    #: bubble elements that will be showed under new message.
    bubble: BubbleMarkup = []

    #: mentions that BotX API will append before new message text.
    mentions: List[Mention] = []
