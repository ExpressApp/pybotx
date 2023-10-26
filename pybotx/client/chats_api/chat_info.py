from datetime import datetime as dt
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.common import ChatNotFoundError
from pybotx.logger import logger
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.chats import ChatInfo, ChatInfoMember
from pybotx.models.enums import (
    APIChatTypes,
    APIUserKinds,
    convert_chat_type_to_domain,
    convert_user_kind_to_domain,
)


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
    creator: Optional[UUID]
    description: Optional[str] = None
    group_chat_id: UUID
    inserted_at: dt
    members: List[Union[BotXAPIChatInfoMember, Dict[str, Any]]]  # noqa: WPS234
    name: str
    shared_history: bool


class BotXAPIChatInfoResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIChatInfoResult

    def to_domain(self) -> ChatInfo:
        if any(isinstance(member, dict) for member in self.result.members):
            logger.warning("One or more unsupported user types skipped")

        members = [
            ChatInfoMember(
                is_admin=member.admin,
                huid=member.user_huid,
                kind=convert_user_kind_to_domain(member.user_kind),
            )
            for member in self.result.members
            if isinstance(member, BotXAPIChatInfoMember)
        ]

        return ChatInfo(
            chat_type=convert_chat_type_to_domain(self.result.chat_type),
            creator_id=self.result.creator,
            description=self.result.description,
            chat_id=self.result.group_chat_id,
            created_at=self.result.inserted_at,
            members=members,
            name=self.result.name,
            shared_history=self.result.shared_history,
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

        return self._verify_and_extract_api_model(
            BotXAPIChatInfoResponsePayload,
            response,
        )
