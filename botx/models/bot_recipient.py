from dataclasses import dataclass
from uuid import UUID


@dataclass
class BotRecipient:
    id: UUID
    host: str
