from datetime import datetime as dt
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import ConfigDict, ValidationError, field_validator, Field
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


class BotXAPIPersonalChatRequestPayload(UnverifiedPayloadBaseModel):
    """Payload запроса на получение персонального чата по HUID пользователя."""

    user_huid: UUID

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def from_domain(cls, user_huid: UUID) -> "BotXAPIPersonalChatRequestPayload":
        return cls(user_huid=user_huid)

    def as_query_params(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")


class BotXAPIPersonalChatMember(VerifiedPayloadBaseModel):
    """Информация об участнике чата."""

    admin: bool
    user_huid: UUID
    user_kind: APIUserKinds

    model_config = ConfigDict(extra="forbid")


class BotXAPIPersonalChatResult(VerifiedPayloadBaseModel):
    """Результат API-ответа по персональному чату."""

    chat_type: APIChatTypes
    creator: Optional[UUID]
    description: Optional[str] = None
    group_chat_id: UUID
    inserted_at: dt
    members: List[Union[BotXAPIPersonalChatMember, Dict[str, Any]]] = Field(
        default_factory=list
    )
    name: str
    shared_history: bool

    model_config = ConfigDict(extra="forbid")

    @field_validator("members", mode="before")
    @classmethod
    def validate_members(
        cls,
        value: List[Union[BotXAPIPersonalChatMember, Dict[str, Any]]],
        info: Any,
    ) -> List[Union[BotXAPIPersonalChatMember, Dict[str, Any]]]:
        return cls._parse_members(value)

    @staticmethod
    def _parse_members(
        members_data: List[Union[BotXAPIPersonalChatMember, Dict[str, Any]]],
    ) -> List[Union[BotXAPIPersonalChatMember, Dict[str, Any]]]:
        # Явная аннотация решает проблему инвариантности List в mypy
        parsed: List[Union[BotXAPIPersonalChatMember, Dict[str, Any]]] = []
        for item in members_data:
            if isinstance(item, dict):
                try:
                    parsed.append(BotXAPIPersonalChatMember.model_validate(item))
                except ValidationError:
                    logger.warning("Unsupported member structure encountered: %s", item)
                    parsed.append(item)
            elif isinstance(item, BotXAPIPersonalChatMember):
                parsed.append(item)
            else:
                logger.warning("Unknown member type: %s", item)
        return parsed


class BotXAPIPersonalChatResponsePayload(VerifiedPayloadBaseModel):
    """Обработанный payload успешного ответа API по персональному чату."""

    status: Literal["ok"]
    result: BotXAPIPersonalChatResult

    model_config = ConfigDict(extra="forbid")

    def to_domain(self) -> ChatInfo:
        members: List[ChatInfoMember] = []
        for member in self.result.members:
            if isinstance(member, BotXAPIPersonalChatMember):
                try:
                    members.append(
                        ChatInfoMember(
                            is_admin=member.admin,
                            huid=member.user_huid,
                            kind=convert_user_kind_to_domain(member.user_kind),
                        )
                    )
                except Exception as exc:
                    logger.warning("Failed to convert member kind: %s", exc)
            else:
                logger.warning(
                    "Unsupported user type skipped in members list: %s", member
                )

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


class PersonalChatMethod(AuthorizedBotXMethod):
    """Метод получения информации о персональном чате по HUID пользователя."""

    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        404: response_exception_thrower(ChatNotFoundError),
    }

    async def execute(
        self,
        payload: BotXAPIPersonalChatRequestPayload,
    ) -> BotXAPIPersonalChatResponsePayload:
        path = "/api/v1/botx/chats/personal"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
            params=payload.as_query_params(),
        )

        return self._verify_and_extract_api_model(
            BotXAPIPersonalChatResponsePayload,
            response,
        )
