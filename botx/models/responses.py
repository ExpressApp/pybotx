"""pydantic models for responses from BotX API."""

from typing import Dict, List, Optional
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


class StealthResponse(BaseModel):
    """Entity that will be returned from BotX API as a result of set/unset stealth"""

    status: Statuses = Statuses.ok
    """operation status"""
    result: Optional[bool] = None
    """operation result."""
    reason: Optional[str] = None
    """reason of error."""
    errors: Optional[List[str]] = None
    """list of errors."""
    error_data: Optional[Dict[str, str]] = None
    """error data."""


class AddRemoveUserResponse(BaseModel):
    """Entity that will be returned from BotX API as a result of add/remove users"""

    status: Statuses = Statuses.ok
    """operation status"""
    result: Optional[bool] = None
    """operation result."""
    reason: Optional[str] = None
    """reason of error."""
    errors: Optional[List[str]] = None
    """list of errors"""
    error_data: Optional[Dict[str, str]] = None
    """error data"""
