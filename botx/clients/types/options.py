"""Special options for messages from bot."""
from pydantic import BaseModel

from botx.models.messages.sending.options import NotificationOptions


class ResultOptions(BaseModel):
    """Configuration for command result or notification that is send to BotX API."""

    #: send message only when stealth mode is enabled.
    stealth_mode: bool = False

    #: don't show next user messages in chat
    silent_response: bool = False

    #: message options for configuring notifications.
    notification_opts: NotificationOptions = NotificationOptions()
