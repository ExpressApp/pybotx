"""Entities that are used in sending operations."""

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

    text: str = Field("", max_length=MAXIMUM_TEXT_LENGTH)
    """message text."""
    file: Optional[File] = None
    """attached to message file."""
    markup: MessageMarkup = MessageMarkup()
    """message markup."""
    options: MessageOptions = MessageOptions()
    """message configuration."""


class UpdatePayload(BaseModel):
    """Payload for message edition."""

    text: Optional[str] = Field(None, max_length=MAXIMUM_TEXT_LENGTH)
    """new message text."""
    keyboard: Optional[KeyboardMarkup] = None
    """new message bubbles."""
    bubbles: Optional[BubbleMarkup] = None
    """new message keyboard."""
    mentions: Optional[List[Mention]] = None
    """new message mentions."""
    opts: Optional[NotificationOptions] = None
    """new message options."""

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
