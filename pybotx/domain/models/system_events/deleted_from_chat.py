from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase
from pybotx.domain.models.chats import Chat


@dataclass(slots=True)
class DeletedFromChatEvent(BotCommandBase):
    """Event `system:deleted_from_chat`.

    Attributes:
        huids: List of deleted from chat user huids.
        chat_id: Chat where the user was deleted from.
    """

    huids: list[UUID]
    chat: Chat
