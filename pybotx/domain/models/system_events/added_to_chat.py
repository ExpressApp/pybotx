from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase
from pybotx.domain.models.chats import Chat


@dataclass(slots=True)
class AddedToChatEvent(BotCommandBase):
    """Event `system:added_to_chat`.

    Attributes:
        huids: List of added to chat user huids.
    """

    huids: list[UUID]
    chat: Chat
