from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from botx.bot.api.commands.base import BotAPIBaseCommand, BotAPIChatEventSender
from botx.bot.api.enums import BotAPICommandTypes, BotAPIUserKinds, convert_user_kind
from botx.bot.models.commands.system_events.chat_created import (
    ChatCreatedEvent,
    ChatCreatedMember,
)
from botx.shared_models.api_base import APIBaseModel
from botx.shared_models.enums import APIChatTypes, convert_chat_type_to_domain

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotAPIChatMember(APIBaseModel):
    is_admin: bool = Field(..., alias="admin")
    huid: UUID
    name: Optional[str]
    user_kind: BotAPIUserKinds


class BotAPIChatCreatedData(APIBaseModel):
    chat_type: APIChatTypes
    creator: UUID
    group_chat_id: UUID
    members: List[BotAPIChatMember]
    name: str


class BotAPIChatCreatedPayload(APIBaseModel):
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

        return ChatCreatedEvent(
            sync_id=self.sync_id,
            chat_id=self.payload.data.group_chat_id,
            bot_id=self.bot_id,
            host=self.sender.host,
            chat_name=self.payload.data.name,
            chat_type=convert_chat_type_to_domain(self.payload.data.chat_type),
            creator_id=self.payload.data.creator,
            members=members,
            raw_command=raw_command,
        )
