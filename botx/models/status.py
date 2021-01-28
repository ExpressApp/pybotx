"""Module of model for status recipient."""
from typing import Optional
from uuid import UUID

from botx import ChatTypes
from botx.models.base import BotXBaseModel


class StatusRecipient(BotXBaseModel):
    """Model of recipients in status request."""

    #: bot that request status
    bot_id: UUID

    #: user that request status
    user_huid: UUID

    #: user's ad_login
    ad_login: Optional[str]

    #: user's ad_domain
    ad_domain: Optional[str]

    #: user has admin role
    is_admin: Optional[bool]

    #: chat type
    chat_type: ChatTypes
