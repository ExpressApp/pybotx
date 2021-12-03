from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from botx.models.api_base import VerifiedPayloadBaseModel
from botx.models.base_command import (
    BotAPIBaseCommand,
    BotAPIChatContext,
    BotCommandBase,
)
from botx.models.chats import Chat
from botx.models.enums import (
    APIChatTypes,
    APIUserKinds,
    BotAPICommandTypes,
    UserKinds,
    convert_chat_type_to_domain,
    convert_user_kind,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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


class BotAPIChatCreatedPayload(VerifiedPayloadBaseModel):
    body: Literal["system:chat_created"] = "system:chat_created"
    command_type: Literal[BotAPICommandTypes.SYSTEM]
    data: BotAPIChatCreatedData
    metadata: Dict[str, Any]


class BotAPIChatCreated(BotAPIBaseCommand):
    payload: BotAPIChatCreatedPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")

    def to_domain(self, raw_command: Dict[str, Any]) -> ChatCreatedEvent:
        members = [
            ChatCreatedMember(
                is_admin=member.is_admin,
                huid=member.huid,
                username=member.name,
                kind=convert_user_kind(member.user_kind),
            )
            for member in self.payload.data.members
        ]

        chat = Chat(
            id=self.payload.data.group_chat_id,
            type=convert_chat_type_to_domain(self.payload.data.chat_type),
            host=self.sender.host,
        )

        return ChatCreatedEvent(
            sync_id=self.sync_id,
            bot_id=self.bot_id,
            chat=chat,
            chat_name=self.payload.data.name,
            creator_id=self.payload.data.creator,
            members=members,
            raw_command=raw_command,
        )