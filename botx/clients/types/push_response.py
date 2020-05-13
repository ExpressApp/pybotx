from uuid import UUID

from pydantic import BaseModel


class PushResult(BaseModel):
    """Entity that contains result from notification or command result push."""

    sync_id: UUID
    """event id of pushed message."""
