from typing import Any, Literal
from uuid import UUID

from pydantic import Field

from pybotx.presentation.contracts.api_base import VerifiedPayloadBaseModel
from pybotx.presentation.contracts.base_command import (
    BotAPIBaseCommand,
    BotAPIBaseSystemEventPayload,
    BotAPIChatContext,
)
from pybotx.presentation.contracts.enums import (
    APIChatTypes,
    APIUserKinds,
    BotAPISystemEventTypes,
    convert_chat_type_to_domain,
    convert_user_kind_to_domain,
)
from pybotx.domain.models.bot_account import BotAccount
from pybotx.domain.models.chats import Chat
from pybotx.domain.models.system_events.chat_created import (
    ChatCreatedEvent,
    ChatCreatedMember,
)


class BotAPIChatMember(VerifiedPayloadBaseModel):
    is_admin: bool = Field(..., alias="admin")
    huid: UUID
    name: str | None
    user_kind: APIUserKinds


class BotAPIChatCreatedData(VerifiedPayloadBaseModel):
    chat_type: APIChatTypes
    creator: UUID
    group_chat_id: UUID
    members: list[BotAPIChatMember]
    name: str


class BotAPIChatCreatedPayload(BotAPIBaseSystemEventPayload):
    body: Literal[BotAPISystemEventTypes.CHAT_CREATED]
    data: BotAPIChatCreatedData


class BotAPIChatCreated(BotAPIBaseCommand):
    payload: BotAPIChatCreatedPayload = Field(..., alias="command")
    sender: BotAPIChatContext = Field(..., alias="from")

    def to_domain(self, raw_command: dict[str, Any]) -> ChatCreatedEvent:
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
