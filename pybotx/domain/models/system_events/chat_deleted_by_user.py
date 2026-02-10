from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase


@dataclass(slots=True)
class ChatDeletedByUserEvent(BotCommandBase):
    """Event `system:chat_deleted_by_user`.

    Attributes:
        sync_id: Event sync id.
        chat_id: Deleted chat id.
        huid: huid of the deleter.
    """

    sync_id: UUID
    chat_id: UUID
    huid: UUID
