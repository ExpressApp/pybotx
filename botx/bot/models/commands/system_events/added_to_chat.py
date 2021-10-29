from dataclasses import dataclass
from typing import List
from uuid import UUID

from botx.bot.models.commands.base import BotCommandBase


@dataclass
class AddedToChatEvent(BotCommandBase):
    """Event `system:added_to_chat`.

    Attributes:
        huids: List of added to chat user huids.
    """

    huids: List[UUID]
