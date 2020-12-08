"""Module of model for status recipient."""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from botx import ChatTypes


class StatusRecipient(BaseModel):
    """Model of recipients in status request."""

    bot_id: UUID
    user_huid: UUID
    ad_login: Optional[str]
    ad_domain: Optional[str]
    is_admin: Optional[bool]
    chat_type: ChatTypes
