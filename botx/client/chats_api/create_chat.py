from typing import List, Optional
from uuid import UUID

from botx.api_base_models import APIBaseModel
from botx.bot.models.commands.enums import ChatTypes
from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.client.enums import BotXAPIChatTypes, convert_chat_type_from_domain

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


class BotXAPICreateChatPayload(APIBaseModel):
    name: str
    description: Optional[str] = None
    chat_type: BotXAPIChatTypes
    members: List[UUID]
    shared_history: bool = False

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


class CreateChatMethod(AuthorizedBotXMethod):
    async def execute(self, payload: BotXAPICreateChatPayload) -> BotXAPIChatId:
        path = "/api/v3/botx/chats/create"

        response = await self._botx_method_call(
            "POST",
            self._build_url(path),
            content=payload.json(),
        )

        return self._extract_api_model(BotXAPIChatId, response)
