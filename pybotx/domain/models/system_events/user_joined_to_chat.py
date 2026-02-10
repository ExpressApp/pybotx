from dataclasses import dataclass
from uuid import UUID

from pybotx.domain.models.base_command import BotCommandBase
from pybotx.domain.models.chats import Chat


@dataclass(slots=True)
class JoinToChatEvent(BotCommandBase):
    """Domain model for user joined to chat event.

    This model represents the domain entity for system:user_joined_to_chat events
    after being converted from the API representation.

    Attributes:
        bot: The bot account that received the event.
        raw_command: The original raw command dictionary.
        huids: List of UUIDs of users who joined the chat.
        chat: The chat that users joined.
    """

    huids: list[UUID]
    chat: Chat
