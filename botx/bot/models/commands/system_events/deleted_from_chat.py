from dataclasses import dataclass
from typing import List
from uuid import UUID

from botx.bot.models.commands.base import BotCommandBase


@dataclass
class DeletedFromChatEvent(BotCommandBase):
    """Event `system:deleted_from_chat`.

    Attributes:
        huids: List of deleted from chat user huids.
    """

    huids: List[UUID]
