from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from botx.bot.api.commands.base import BotAPIBaseCommand, BotAPIChatEventSender
from botx.bot.api.enums import BotAPICommandTypes
from botx.bot.models.commands.chat import Chat
from botx.bot.models.commands.system_events.chat_created import (
    ChatCreatedEvent,
    ChatCreatedMember,
)
from botx.shared_models.api.enums import APIUserKinds, convert_user_kind
from botx.shared_models.api_base import VerifiedPayloadBaseModel
from botx.shared_models.chat_types import APIChatTypes, convert_chat_type_to_domain

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


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
    sender: BotAPIChatEventSender = Field(..., alias="from")

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
