from dataclasses import dataclass
from typing import List
from uuid import UUID

from botx.bot.models.commands.base import BotCommandBase
from botx.bot.models.commands.chat import Chat


@dataclass
class DeletedFromChatEvent(BotCommandBase):
    """Event `system:deleted_from_chat`.

    Attributes:
        huids: List of deleted from chat user huids.
        chat_id: Chat where the user was deleted from.
    """

    huids: List[UUID]
    chat: Chat
