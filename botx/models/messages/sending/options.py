"""Special options for message."""

from typing import List

from pydantic import BaseModel

from botx.models.mentions import Mention
from botx.models.typing import AvailableRecipients


class NotificationOptions(BaseModel):
    """Configurations for message notifications."""

    #: show notification about message.
    send: bool = True

    #: break mute on bot messages.
    force_dnd: bool = False


class MessageOptions(BaseModel):
    """Message options configuration."""

    #: users that should receive message.
    recipients: AvailableRecipients = "all"

    #: attached to message mentions.
    mentions: List[Mention] = []

    #: notification configuration.
    notifications: NotificationOptions = NotificationOptions()
