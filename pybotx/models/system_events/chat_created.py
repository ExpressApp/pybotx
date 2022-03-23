from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional
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
from pybotx.models.enums import (
    APIChatTypes,
    APIUserKinds,
    BotAPISystemEventTypes,
    UserKinds,
    convert_chat_type_to_domain,
    convert_user_kind_to_domain,
)


@dataclass
class ChatCreatedMember:
    """ChatCreatedEvent member.

    Attributes:
        is_admin: Is user admin.
        huid: User huid.
        username: Username.
        kind: User type.
    """

    is_admin: bool
    huid: UUID
    username: Optional[str]
    kind: UserKinds


@dataclass
class ChatCreatedEvent(BotCommandBase):
    """Event `system:chat_created`.

    Attributes:
        sync_id: Event sync id.
        chat_id: Created chat id.
        chat_name: Created chat name.
        chat_type: Created chat type.
        host: Created chat cts host.
        creator_id: Creator huid.
        members: List of created chat members.
    """

    chat: Chat
    sync_id: UUID
    chat_name: str
    creator_id: UUID
    members: List[ChatCreatedMember]


class BotAPIChatMember(VerifiedPayloadBaseModel):
    is_admin: bool = Field(..., alias="admin")
    huid: UUID
    name: Optional[str]
    user_kind: APIUserKinds


class BotAPIChatCreatedData(VerifiedPayloadBaseModel):
    chat_type: APIChatTypes
    creator: UUID
    group_chat_id: UUID
    members: List[BotAPIChatMember]
    name: str


class BotAPIChatCreatedPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.CHAT_CREATED]
    data: BotAPIChatCreatedData


class BotAPIChatCreated(BotAPIBaseCommand):
    payload: BotAPIChatCreatedPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> ChatCreatedEvent:
        members = [
            ChatCreatedMember(
                is_admin=member.is_admin,
                huid=member.huid,
                username=member.name,
                kind=convert_user_kind_to_domain(member.user_kind),
            )
            for member in self.payload.data.members
        ]

        chat = Chat(
            id=self.payload.data.group_chat_id,
            type=convert_chat_type_to_domain(self.payload.data.chat_type),
        )

        return ChatCreatedEvent(
            sync_id=self.sync_id,
            bot=BotAccount(
                id=self.bot_id,
                host=self.sender.host,
            ),
            chat=chat,
            chat_name=self.payload.data.name,
            creator_id=self.payload.data.creator,
            members=members,
            raw_command=raw_command,
        )
