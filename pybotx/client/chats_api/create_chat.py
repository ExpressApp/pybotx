from typing import Any, Dict, List, Literal, Optional, Set, Union
from uuid import UUID

from pydantic import (
    Field,
    ConfigDict,
    field_serializer,
    field_validator,
    model_validator,
)

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.client.botx_method import response_exception_thrower
from pybotx.client.exceptions.chats import (
    ChatCreationError,
    ChatCreationProhibitedError,
)
from pybotx.missing import Missing, Undefined
from pybotx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from pybotx.models.attachments import decode_rfc2397
from pybotx.models.enums import APIChatTypes, ChatTypes, convert_chat_type_from_domain


class BotXAPICreateChatRequestPayload(UnverifiedPayloadBaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        frozen=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    chat_type: Union[APIChatTypes, ChatTypes]
    members: List[UUID]
    shared_history: Missing[bool]
    avatar: Optional[str] = None

    @model_validator(mode="before")
    def _convert_chat_type(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        ct = values.get("chat_type")
        if isinstance(ct, ChatTypes):
            values["chat_type"] = convert_chat_type_from_domain(ct)
        return values

    @field_validator("avatar")
    def _validate_avatar(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not v.startswith("data:"):
            raise ValueError("Avatar must be a data URL (RFC2397)")
        try:
            decode_rfc2397(v)
        except Exception as e:
            raise ValueError(f"Invalid data URL format: {e}")
        return v

    @field_serializer("chat_type")
    def _serialize_chat_type(self, v: APIChatTypes) -> str:
        return v.value.lower()


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

        exclude: Set[str] = (
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
