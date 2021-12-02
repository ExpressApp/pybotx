from dataclasses import dataclass
from uuid import UUID

from botx.models.enums import ChatTypes


@dataclass
class Chat:
    id: UUID
    type: ChatTypes
    host: str
