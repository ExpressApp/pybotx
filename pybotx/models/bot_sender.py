from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class BotSender:
    huid: UUID
    is_chat_admin: Optional[bool]
    is_chat_creator: Optional[bool]
