from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase
from pybotx.domain.models.chats import Chat


@dataclass(slots=True)
class LeftFromChatEvent(BotCommandBase):
    """Event `system:left_from_chat`.

    Attributes:
        huids: List of left from chat user huids.
    """

    huids: list[UUID]
    chat: Chat
