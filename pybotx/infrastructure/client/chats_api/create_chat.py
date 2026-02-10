from typing import Any, Literal
from uuid import UUID

from pydantic import (
    Field,
    ConfigDict,
    field_serializer,
    field_validator,
    model_validator,
)

from pybotx.infrastructure.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.infrastructure.client.botx_method import response_exception_thrower
from pybotx.infrastructure.client.exceptions.chats import (
    ChatCreationError,
    ChatCreationProhibitedError,
)
from pybotx.domain.missing import Missing, Undefined
from pybotx.domain.models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)
from pybotx.domain.models.attachments import decode_rfc2397
from pybotx.domain.errors import InvalidAvatarDataError
from pybotx.infrastructure.contracts.enums import (
    APIChatTypes,
    convert_chat_type_from_domain,
)
from pybotx.domain.models.enums import ChatTypes


class BotXAPICreateChatRequestPayload(UnverifiedPayloadBaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        frozen=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    name: str = Field(..., min_length=1)
    description: str | None = None
    chat_type: APIChatTypes | ChatTypes
    members: list[UUID]
    shared_history: Missing[bool]
    avatar: str | None = None

    @model_validator(mode="before")
    def _convert_chat_type(cls, values: dict[str, Any]) -> dict[str, Any]:
        chat_type = values.get("chat_type")
        if isinstance(chat_type, ChatTypes):
            values["chat_type"] = convert_chat_type_from_domain(chat_type)
        return values

    @field_validator("avatar")
    def _validate_avatar(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not v.startswith("data:"):
            raise InvalidAvatarDataError("Avatar must be a data URL (RFC2397)")
        try:
            decode_rfc2397(v)
        except Exception as e:
            raise InvalidAvatarDataError(f"Invalid data URL format: {e}")
        return v

    @field_serializer("chat_type")
    def _serialize_chat_type(self, v: APIChatTypes | ChatTypes) -> str:
        if isinstance(v, ChatTypes):
            v = convert_chat_type_from_domain(v)
        return v.value


class BotXAPIChatIdResult(VerifiedPayloadBaseModel):
    model_config = ConfigDict(frozen=True)
    chat_id: UUID


class BotXAPICreateChatResponsePayload(VerifiedPayloadBaseModel):
    model_config = ConfigDict(frozen=True)
    status: Literal["ok"]
    result: BotXAPIChatIdResult

    def to_domain(self) -> UUID:
        return self.result.chat_id


class CreateChatMethod(AuthorizedBotXMethod):
    status_handlers = {
        **AuthorizedBotXMethod.status_handlers,
        403: response_exception_thrower(ChatCreationProhibitedError),
        422: response_exception_thrower(ChatCreationError),
    }

    async def execute(
        self,
        payload: BotXAPICreateChatRequestPayload,
    ) -> BotXAPICreateChatResponsePayload:
        """
        Создаёт чат через BotX API.
        """
        url = self._build_url("/api/v3/botx/chats/create")

        exclude: set[str] = (
            {"shared_history"} if payload.shared_history is Undefined else set()
        )

        body = payload.model_dump(mode="json", exclude=exclude)

        response = await self._botx_method_call(
            "POST",
            url,
            json=body,
        )

        return self._verify_and_extract_api_model(
            BotXAPICreateChatResponsePayload,
            response,
        )
