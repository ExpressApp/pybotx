"""Entities for chats."""

from typing import Iterator, List, Optional
from uuid import UUID
from datetime import datetime

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

    #: creation datetime of chat.
    inserted_at: datetime


class BotChat(BotXBaseModel):
    #: name of chat.
    name: str

    #: description of chat
    description: Optional[str]

    #: type of chat.
    chat_type: ChatTypes

    #: ID of chat.
    group_chat_id: UUID

    #: users in chat.
    members: List[UUID]

    #: creation datetime of chat.
    inserted_at: datetime

    #: update datetime of chat.
    updated_at: datetime


class BotChatList(BotXBaseModel):
    __root__: List[BotChat]

    def __iter__(self) -> Iterator[BotChat]:  # noqa: D105
        return iter(self.__root__)

    def __len__(self) -> int:  # noqa: D105
        return len(self.__root__)

    def __getitem__(self, key: int) -> BotChat:  # noqa: D105
        return self.__root__[key]
