from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class BotSender:
    huid: UUID
    is_chat_admin: bool | None
    is_chat_creator: bool | None
