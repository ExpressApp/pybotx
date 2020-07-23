"""Shape that is used for messages from bot."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from botx.models.constants import MAXIMUM_TEXT_LENGTH
from botx.models.enums import Statuses
from botx.models.mentions import Mention
from botx.models.typing import BubbleMarkup, KeyboardMarkup

try:
    from typing import Literal  # noqa: WPS433
except ImportError:
    from typing_extensions import (  # type: ignore  # noqa: WPS433, WPS440, F401
        Literal,
    )


class ResultPayload(BaseModel):
    """Data that is sent when bot answers on command or send notification."""

    #: status of operation.
    status: Literal[Statuses.ok] = Statuses.ok

    #: body for new message from bot.
    body: str = Field("", max_length=MAXIMUM_TEXT_LENGTH)

    #: message metadata.
    metadata: Dict[str, Any] = {}

    #: keyboard that will be used for new message.
    keyboard: KeyboardMarkup = []

    #: bubble elements that will be showed under new message.
    bubble: BubbleMarkup = []

    #: mentions that BotX API will append before new message text.
    mentions: List[Mention] = []


class UpdatePayload(BaseModel):
    """Data that is sent when bot updates message."""

    #: status of operation.
    status: Literal[Statuses.ok] = Statuses.ok

    #: new body in message.
    body: Optional[str] = Field(None, max_length=MAXIMUM_TEXT_LENGTH)

    #: new keyboard that will be used for new message.
    keyboard: Optional[KeyboardMarkup] = None

    #: new bubble elements that will be showed under new message.
    bubble: Optional[BubbleMarkup] = None

    #: new mentions that BotX API will append before new message text.
    mentions: Optional[List[Mention]] = None
