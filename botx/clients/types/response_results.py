"""Responses from BotX API."""
from uuid import UUID

from pydantic import BaseModel


class PushResult(BaseModel):
    """Entity that contains result from notification or command result push."""

    #: event id of pushed message.
    sync_id: UUID


class ChatCreatedResult(BaseModel):
    """Entity that contains result from chat creation."""

    #: id of created chat.
    chat_id: UUID


class InternalBotNotificationResult(BaseModel):
    """Entity that contains result from internal bot notification."""

    #: event id of pushed message.
    sync_id: UUID
