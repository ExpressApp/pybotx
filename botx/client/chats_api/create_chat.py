from typing import List, Literal, Optional
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import response_exception_thrower
from botx.client.exceptions.chats import ChatCreationError, ChatCreationProhibitedError
from botx.missing import Missing
from botx.models.api_base import UnverifiedPayloadBaseModel, VerifiedPayloadBaseModel
from botx.models.enums import APIChatTypes, ChatTypes, convert_chat_type_from_domain


class BotXAPICreateChatRequestPayload(UnverifiedPayloadBaseModel):
    name: str
    description: Optional[str]
    chat_type: APIChatTypes
    members: List[UUID]
    shared_history: Missing[bool]

    @classmethod
    def from_domain(
        cls,
        name: str,
        chat_type: ChatTypes,
        huids: List[UUID],
        shared_history: Missing[bool],
        description: Optional[str] = None,
    ) -> "BotXAPICreateChatRequestPayload":
        return cls(
            name=name,
            chat_type=convert_chat_type_from_domain(chat_type),
            members=huids,
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

        return self._verify_and_extract_api_model(
            BotXAPICreateChatResponsePayload,
            response,
        )
