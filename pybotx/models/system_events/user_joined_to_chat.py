from dataclasses import dataclass
from typing import Any, Dict, List, Literal
from uuid import UUID

from pydantic import Field

from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
    BotAPIChatContext,
    BotCommandBase,
)
from pybotx.models.bot_account import BotAccount
from pybotx.models.chats import Chat
from pybotx.models.enums import BotAPISystemEventTypes, convert_chat_type_to_domain


@dataclass
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

    huids: List[UUID]
    chat: Chat


class BotAPIJoinToChatData(VerifiedPayloadBaseModel):
    """Data model for user joined to chat event.

    This model represents the data field in the BotX API payload
    for system:user_joined_to_chat events.

    Attributes:
        added_members: List of UUIDs of users who joined the chat.
    """

    added_members: List[UUID]


class BotAPIJoinToChatPayload(BotAPIBaseSystemEventPayload):
    """Payload model for user joined to chat event.

    This model represents the command field in the BotX API request
    for system:user_joined_to_chat events.

    Attributes:
        body: Literal value of BotAPISystemEventTypes.JOIN_TO_CHAT.
        data: The data containing information about users who joined.
    """

    body: Literal[BotAPISystemEventTypes.JOIN_TO_CHAT]
    data: BotAPIJoinToChatData


class BotAPIJoinToChat(BotAPIBaseCommand):
    """API model for user joined to chat event.

    This model represents the complete BotX API request structure
    for system:user_joined_to_chat events.

    Attributes:
        payload: The command payload with event data.
        sender: The chat context information.
    """

    payload: BotAPIJoinToChatPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> JoinToChatEvent:
        return JoinToChatEvent(
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            raw_command=raw_command,
            huids=self.payload.data.added_members,
            chat=Chat(
                id=self.sender.group_chat_id,
                type=convert_chat_type_to_domain(self.sender.chat_type),
            ),
        )

    class Config:
        allow_population_by_field_name = True
