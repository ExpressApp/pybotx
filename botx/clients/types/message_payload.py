"""Shape that is used for messages from bot."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from botx.models.constants import MAXIMUM_TEXT_LENGTH
from botx.models.entities import Mention
from botx.models.enums import Statuses
from botx.models.messages.sending.options import ResultPayloadOptions
from botx.models.typing import BubbleMarkup, KeyboardMarkup

try:
    from typing import Literal  # noqa: WPS433
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS433, WPS440, F401


class ResultPayload(BaseModel):
    """Data that is sent when bot answers on command or send notification."""

    #: status of operation.
    status: Literal[Statuses.ok] = Statuses.ok

    #: body for new message from bot.
    body: str = Field("", max_length=MAXIMUM_TEXT_LENGTH)

    #: message metadata.
    metadata: Dict[str, Any] = {}

    #: options for `notification` and `command_result` API entities.
    opts: ResultPayloadOptions = ResultPayloadOptions()

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

    #: message metadata.
    metadata: Optional[Dict[str, Any]] = None

    #: new keyboard that will be used for new message.
    keyboard: Optional[KeyboardMarkup] = None

    #: new bubble elements that will be showed under new message.
    bubble: Optional[BubbleMarkup] = None

    #: new mentions that BotX API will append before new message text.
    mentions: Optional[List[Mention]] = None


class InternalBotNotificationPayload(BaseModel):
    """Data that is sent in internal bot notification."""

    #: message data
    message: str

    #: extra information about notification sender
    sender: Optional[str]
