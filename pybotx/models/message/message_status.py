from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class MessageStatus:
    group_chat_id: UUID
    sent_to: list[UUID]
    read_by: dict[UUID, datetime]
    received_by: dict[UUID, datetime]
