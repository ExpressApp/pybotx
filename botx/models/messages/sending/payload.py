"""Payload for messages."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import Field

from botx.models.base import BotXBaseModel
from botx.models.constants import MAXIMUM_TEXT_LENGTH
from botx.models.entities import Mention
from botx.models.files import File
from botx.models.messages.sending.markup import MessageMarkup
from botx.models.messages.sending.options import MessageOptions, NotificationOptions
from botx.models.typing import BubbleMarkup, KeyboardMarkup


class MessagePayload(BotXBaseModel):
    """Message payload configuration."""

    #: message text.
    text: str = Field("", max_length=MAXIMUM_TEXT_LENGTH)

    #: message metadata.
    metadata: Dict[str, Any] = {}

    #: file attached to message.
    file: Optional[File] = None

    #: message markup.
    markup: MessageMarkup = MessageMarkup()

    #: message configuration.
    options: MessageOptions = MessageOptions()


class UpdatePayload(BotXBaseModel):
    """Payload for message edition."""

    #: new message text.
    text: Optional[str] = Field(None, max_length=MAXIMUM_TEXT_LENGTH)

    #: file attached to message.
    file: Optional[File] = None

    #: new message bubbles.
    keyboard: Optional[KeyboardMarkup] = None

    #: new message keyboard.
    bubbles: Optional[BubbleMarkup] = None

    #: new message mentions.
    mentions: Optional[List[Mention]] = None

    #: new message options.
    opts: Optional[NotificationOptions] = None

    #: message metadata.
    metadata: Optional[Dict[str, Any]] = None

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

    @classmethod
    def from_sending_payload(cls, payload: MessagePayload) -> UpdatePayload:
        """Create new update payload from existing payload for new message.

        Arguments:
            payload: payload that can be used for sending new message.

        Returns:
            Created payload for update.
        """
        update = cls()
        update.text = payload.text or None
        update.set_markup(payload.markup)
        update.mentions = payload.options.mentions
        update.file = payload.file
        update.metadata = payload.metadata
        return update
