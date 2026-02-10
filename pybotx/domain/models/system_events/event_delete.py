from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase


@dataclass(slots=True)
class EventDeleted(BotCommandBase):
    """Event `system:event_deleted`.

    Attributes:
        deleted_at: Delete message date and time.
        group_chat_id: Delete message group chat id.
        meta: Delete message meta.
        sync_ids: Delete message sync ids.
    """

    deleted_at: datetime
    group_chat_id: UUID
    sync_ids: list[UUID]
    meta: dict[str, Any] | None
