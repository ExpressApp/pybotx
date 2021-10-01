from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from botx.shared_models.chat_types import ChatTypes


@dataclass
class StatusRecipient:
    bot_id: UUID
    huid: UUID
    ad_login: Optional[str]
    ad_domain: Optional[str]
    is_admin: bool
    chat_type: ChatTypes
