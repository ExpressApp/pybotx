from typing import List

from pydantic import BaseModel

from botx.models.mentions import Mention
from botx.models.typing import AvailableRecipients


class NotificationOptions(BaseModel):
    """Configurations for message notifications."""

    send: bool = True
    """show notification about message."""
    force_dnd: bool = False
    """break mute on bot messages."""


class MessageOptions(BaseModel):
    """Message options configuration."""

    recipients: AvailableRecipients = "all"
    """users that should receive message."""
    mentions: List[Mention] = []
    """attached to message mentions."""
    notifications: NotificationOptions = NotificationOptions()
    """notification configuration."""
