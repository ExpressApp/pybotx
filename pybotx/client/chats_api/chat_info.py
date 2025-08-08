from datetime import datetime as dt
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import ConfigDict, ValidationError, field_validator
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

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def from_domain(cls, chat_id: UUID) -> "BotXAPIChatInfoRequestPayload":
        return cls(group_chat_id=chat_id)

    def as_query_params(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")


class BotXAPIChatInfoMember(VerifiedPayloadBaseModel):
    admin: bool
    user_huid: UUID
    user_kind: APIUserKinds

    model_config = ConfigDict(extra="ignore")


class BotXAPIChatInfoResult(VerifiedPayloadBaseModel):
    chat_type: APIChatTypes
    creator: Optional[UUID]
    description: Optional[str] = None
    group_chat_id: UUID
    inserted_at: dt
    members: List[Union[BotXAPIChatInfoMember, Dict[str, Any]]] = []
    name: str
    shared_history: bool

    model_config = ConfigDict(extra="ignore")

    @staticmethod
    def validate_members(
        items: List[Union[BotXAPIChatInfoMember, Dict[str, Any]]],
        info: Any,
    ) -> List[Union[BotXAPIChatInfoMember, Dict[str, Any]]]:
        """
        Публичный helper для парсинга списка участников:
        - dict → BotXAPIChatInfoMember
        - уже готовый BotXAPIChatInfoMember остаётся как есть
        - всё остальное логируется и пропускается
        """
        parsed: List[Union[BotXAPIChatInfoMember, Dict[str, Any]]] = []
        for item in items:
            if isinstance(item, dict):
                try:
                    parsed.append(BotXAPIChatInfoMember.model_validate(item))
                except ValidationError:
                    # Сохраняем оригинал, чтобы downstream-логика могла
                    # увидеть и обработать «неожиданную» структуру
                    parsed.append(item)
                    logger.warning("Unsupported member structure encountered: %s", item)
            elif isinstance(item, BotXAPIChatInfoMember):
                parsed.append(item)
            else:
                logger.warning("Unknown member type: %s", item)  # pragma: no cover
        return parsed

    @field_validator("members", mode="before")
    @classmethod
    def _validate_members_field(
        cls,
        value: List[Union[BotXAPIChatInfoMember, Dict[str, Any]]],
        info: Any,
    ) -> List[Union[BotXAPIChatInfoMember, Dict[str, Any]]]:
        return cls.validate_members(value, info)


class BotXAPIChatInfoResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: BotXAPIChatInfoResult

    model_config = ConfigDict(extra="ignore")

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
            params=payload.as_query_params(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIChatInfoResponsePayload,
            response,
        )
