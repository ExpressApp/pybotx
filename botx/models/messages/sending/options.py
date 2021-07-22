"""Special options for message."""

from typing import List

from botx.models.base import BotXBaseModel
from botx.models.entities import Mention
from botx.models.typing import AvailableRecipients


class ResultPayloadOptions(BotXBaseModel):
    """Options for `notification` and `command_result` API entities."""

    #: don't show next user's input in chat
    silent_response: bool = False


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

    #: don't show next user's input in chat
    silent_response: bool = False

    #: deliver message only if stealth mode enabled
    stealth_mode: bool = False

    #: use in-text mentions
    raw_mentions: bool = False

    #: notification configuration.
    notifications: NotificationOptions = NotificationOptions()
