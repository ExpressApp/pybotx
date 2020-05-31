"""Payload for messages."""

from typing import List, Optional

from pydantic import BaseModel, Field

from botx.models.constants import MAXIMUM_TEXT_LENGTH
from botx.models.files import File
from botx.models.mentions import Mention
from botx.models.messages.sending.markup import MessageMarkup
from botx.models.messages.sending.options import MessageOptions, NotificationOptions
from botx.models.typing import BubbleMarkup, KeyboardMarkup


class MessagePayload(BaseModel):
    """Message payload configuration."""

    #: message text.
    text: str = Field("", max_length=MAXIMUM_TEXT_LENGTH)

    #: attached to message file.
    file: Optional[File] = None

    #: message markup.
    markup: MessageMarkup = MessageMarkup()

    #: message configuration.
    options: MessageOptions = MessageOptions()


class UpdatePayload(BaseModel):
    """Payload for message edition."""

    #: new message text.
    text: Optional[str] = Field(None, max_length=MAXIMUM_TEXT_LENGTH)

    #: new message bubbles.
    keyboard: Optional[KeyboardMarkup] = None

    #: new message keyboard.
    bubbles: Optional[BubbleMarkup] = None

    #: new message mentions.
    mentions: Optional[List[Mention]] = None

    #: new message options.
    opts: Optional[NotificationOptions] = None

    @property
    def markup(self) -> MessageMarkup:
        """Markup for edited message."""
        return MessageMarkup(bubbles=self.bubbles or [], keyboard=self.keyboard or [])

    def set_markup(self, markup: MessageMarkup) -> None:
        """Markup for edited message.

        Arguments:
            markup: markup that should be applied to payload.
        """
        self.bubbles = markup.bubbles
        self.keyboard = markup.keyboard
