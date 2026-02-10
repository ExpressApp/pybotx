from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pybotx.domain.models.enums import ChatTypes


@dataclass(slots=True)
class Forward:
    chat_id: UUID
    author_id: UUID
    sync_id: UUID
    chat_name: str
    forward_type: ChatTypes
    inserted_at: datetime
