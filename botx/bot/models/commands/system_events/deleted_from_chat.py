from dataclasses import dataclass
from typing import List
from uuid import UUID

from botx.bot.models.commands.base import BotCommandBase


@dataclass
class DeletedFromChatEvent(BotCommandBase):
    huids: List[UUID]
