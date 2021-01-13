"""Entities for chats."""

from typing import List, Optional
from uuid import UUID

from botx.models.base import BotXBaseModel
from botx.models.enums import ChatTypes
from botx.models.users import UserFromChatSearch


class ChatFromSearch(BotXBaseModel):
    """Chat from search request."""

    #: name of chat.
    name: str

    #: description of chat
    description: Optional[str]

    #: type of chat.
    chat_type: ChatTypes

    #: HUID of chat creator.
    creator: UUID

    #: ID of chat.
    group_chat_id: UUID

    #: users in chat.
    members: List[UserFromChatSearch]
