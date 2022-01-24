from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
from uuid import UUID


@dataclass
class MessageStatus:
    group_chat_id: UUID
    sent_to: List[UUID]
    read_by: Dict[UUID, datetime]
    received_by: Dict[UUID, datetime]
