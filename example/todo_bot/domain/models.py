from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class TodoItem:
    id: int
    chat_id: UUID
    text: str
    created_at: datetime
    completed_at: datetime | None = None

    @property
    def is_done(self) -> bool:
        return self.completed_at is not None
