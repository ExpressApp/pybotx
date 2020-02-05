"""pydantic models for responses from BotX API."""

from uuid import UUID

from pydantic import BaseModel, Field

from botx.models.enums import Statuses


class TokenResponse(BaseModel):
    """Response form for BotX API token request."""

    result: str
    """obtained token from request to BotX API."""


class PushResult(BaseModel):
    """Entity that contains result from notification or command result push."""

    sync_id: UUID
    """event id of pushed message."""


class PushResponse(BaseModel):
    """Entity that will be returned from BotX API command result push."""

    status: Statuses = Field(Statuses.ok, const=True)
    """operation status of push."""
    result: PushResult
    """operation result."""
