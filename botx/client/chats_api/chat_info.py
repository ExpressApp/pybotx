from dataclasses import dataclass
from datetime import datetime as dt
from typing import List, Optional
from uuid import UUID

from botx.bot.models.commands.enums import UserKinds
from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.exceptions.common import ChatNotFoundError
from botx.shared_models.api.enums import APIUserKinds, convert_user_kind
from botx.shared_models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)
from botx.shared_models.chat_types import (
    APIChatTypes,
    ChatTypes,
    convert_chat_type_to_domain,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class ChatInfoMember:
    """Chat member.

    Attributes:
        is_admin: Is user admin.
        huid: User huid.
        kind: User type.
    """

    is_admin: bool
    huid: UUID
    kind: UserKinds


@dataclass
class ChatInfo:
    """Chat information.

    Attributes:
        chat_type: Chat type.
        creator_id: Chat creator id.
        description: Chat description.
        chat_id: Chat id.
        created_at: Chat creation datetime.
        members: Chat members.
        name: Chat name.
    """

    chat_type: ChatTypes
    creator_id: UUID
    description: Optional[str]
    chat_id: UUID
    created_at: dt
    members: List[ChatInfoMember]
    name: str


class BotXAPIChatInfoRequestPayload(UnverifiedPayloadBaseModel):
    group_chat_id: UUID

    @classmethod
    def from_domain(cls, chat_id: UUID) -> "BotXAPIChatInfoRequestPayload":
        return cls(group_chat_id=chat_id)


class BotXAPIChatInfoMember(VerifiedPayloadBaseModel):
    admin: bool
    user_huid: UUID
    user_kind: APIUserKinds


class BotXAPIChatInfoResult(VerifiedPayloadBaseModel):
    chat_type: APIChatTypes
    creator: UUID
    description: Optional[str] = None
    group_chat_id: UUID
    inserted_at: dt
    members: List[BotXAPIChatInfoMember]
    name: str


class BotXAPIChatInfoResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIChatInfoResult

    def to_domain(self) -> ChatInfo:
        members = [
            ChatInfoMember(
                is_admin=member.admin,
                huid=member.user_huid,
                kind=convert_user_kind(member.user_kind),
            )
            for member in self.result.members
        ]

        return ChatInfo(
            chat_type=convert_chat_type_to_domain(self.result.chat_type),
            creator_id=self.result.creator,
            description=self.result.description,
            chat_id=self.result.group_chat_id,
            created_at=self.result.inserted_at,
            members=members,
            name=self.result.name,
        )


class ChatInfoMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(ChatNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIChatInfoRequestPayload,
    ) -> BotXAPIChatInfoResponsePayload:
        path = "/api/v3/botx/chats/info"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.jsonable_dict(),
        )

        return self._extract_api_model(BotXAPIChatInfoResponsePayload, response)
