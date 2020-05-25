from pydantic import BaseModel

from botx.models.sending import NotificationOptions


class ResultOptions(BaseModel):
    """Configuration for command result or notification that is send to BotX API."""

    stealth_mode: bool = False
    """send message only when stealth mode is enabled"""
    notification_opts: NotificationOptions = NotificationOptions()
    """message options for configuring notifications."""
