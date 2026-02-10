from typing import Protocol
from uuid import UUID


class BotXMethodCallback(Protocol):
    sync_id: UUID
