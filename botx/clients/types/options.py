from pydantic import BaseModel


class NotificationOptions(BaseModel):
    """Configurations for message notifications."""

    send: bool = True
    """show notification about message."""
    force_dnd: bool = False
    """break mute on bot messages."""


class ResultOptions(BaseModel):
    """Configuration for command result or notification that is send to BotX API."""

    stealth_mode: bool = False
    """send message only when stealth mode is enabled"""
    notification_opts: NotificationOptions = NotificationOptions()
    """message options for configuring notifications."""
