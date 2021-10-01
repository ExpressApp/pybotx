from typing import List, NoReturn, Optional
from uuid import UUID

import httpx

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.botx_method import StatusHandlers
from botx.client.exceptions import ChatCreationError, ChatCreationProhibited
from botx.shared_models.api_base import APIBaseModel
from botx.shared_models.enums import (
    APIChatTypes,
    ChatTypes,
    convert_chat_type_from_domain,
)

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPICreateChatPayload(APIBaseModel):
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
    ) -> "BotXAPICreateChatPayload":
        return cls.construct(
            name=name,
            chat_type=convert_chat_type_from_domain(chat_type),
            members=members,
            description=description,
            shared_history=shared_history,
        )


class BotXAPIChatIdResult(APIBaseModel):
    chat_id: UUID


class BotXAPIChatId(APIBaseModel):
    status: Literal["ok"]
    result: BotXAPIChatIdResult

    def to_domain(self) -> UUID:
        return self.result.chat_id


def chat_creation_prohibited_status_error(response: httpx.Response) -> NoReturn:
    raise ChatCreationProhibited(response)


def chat_creation_error_status_handler(response: httpx.Response) -> NoReturn:
    raise ChatCreationError(response)


class CreateChatMethod(AuthorizedBotXMethod):
    status_handlers: StatusHandlers = {  # TODO: Fix this ignore
        **AuthorizedBotXMethod.status_handlers,  # type: ignore
        403: chat_creation_prohibited_status_error,
        422: chat_creation_error_status_handler,
    }

    async def execute(self, payload: BotXAPICreateChatPayload) -> BotXAPIChatId:
        path = "/api/v3/botx/chats/create"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            content=payload.json(),
        )

        return self._extract_api_model(BotXAPIChatId, response)
