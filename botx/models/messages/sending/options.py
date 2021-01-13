"""Special options for message."""

from typing import List

from botx.models.base import BotXBaseModel
from botx.models.entities import Mention
from botx.models.typing import AvailableRecipients


class NotificationOptions(BotXBaseModel):
    """Configurations for message notifications."""

    #: show notification about message.
    send: bool = True

    #: break mute on bot messages.
    force_dnd: bool = False


class MessageOptions(BotXBaseModel):
    """Message options configuration."""

    #: users that should receive message.
    recipients: AvailableRecipients = "all"

    #: attached to message mentions.
    mentions: List[Mention] = []

    #: if true don't show next user's input in chat
    silent_response: bool = False

    #: notification configuration.
    notifications: NotificationOptions = NotificationOptions()
