from dataclasses import dataclass
from uuid import UUID

from botx.shared_models.chat_types import ChatTypes


@dataclass
class Chat:
    id: UUID
    type: ChatTypes
    host: str
