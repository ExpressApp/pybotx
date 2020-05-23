from uuid import UUID

from pydantic import BaseModel


class PushResult(BaseModel):
    """Entity that contains result from notification or command result push."""

    sync_id: UUID
    """event id of pushed message."""


class ChatCreatedResult(BaseModel):
    """Entity that contains result from chat creation."""

    chat_id: UUID
    """id of created chat."""
