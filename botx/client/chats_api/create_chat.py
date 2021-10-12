from typing import List, Optional
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.chats_api.exceptions import (
    ChatCreationError,
    ChatCreationProhibitedError,
)
from botx.shared_models.api.enums import APIChatTypes, convert_chat_type_from_domain
from botx.shared_models.api_base import (
    UnverifiedPayloadBaseModel,
    VerifiedPayloadBaseModel,
)
from botx.shared_models.domain.enums import ChatTypes

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPICreateChatRequestPayload(UnverifiedPayloadBaseModel):
    name: str
    description: Optional[str]
    chat_type: APIChatTypes
    members: List[UUID]
    shared_history: bool

    @classmethod
    def from_domain(
        cls,
        name: str,
        chat_type: ChatTypes,
        members: List[UUID],
        description: Optional[str] = None,
        shared_history: bool = False,
    ) -> "BotXAPICreateChatRequestPayload":
        return cls(
            name=name,
            chat_type=convert_chat_type_from_domain(chat_type),
            members=members,
            description=description,
            shared_history=shared_history,
        )


class BotXAPIChatIdResult(VerifiedPayloadBaseModel):
    chat_id: UUID


class BotXAPICreateChatResponsePayload(VerifiedPayloadBaseModel):
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
        path = "/api/v3/botx/chats/create"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            json=payload.jsonable_dict(),
        )

        return self._extract_api_model(BotXAPICreateChatResponsePayload, response)
