from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from botx.api_base_models import APIBaseModel
from botx.bot.api.enums import BotAPIChatTypes, convert_chat_type_to_domain
from botx.bot.models.commands.enums import ChatTypes
from botx.client.authorized_botx_method import AuthorizedBotXMethod

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class ChatListItem:
    chat_id: UUID
    chat_type: ChatTypes
    name: str
    description: Optional[str]
    members: List[UUID]
    inserted_at: datetime
    updated_at: datetime


class BotXAPIListChatResult(APIBaseModel):
    group_chat_id: UUID
    chat_type: BotAPIChatTypes  # FIXME: Change to BotXAPIChatTypes
    name: str
    description: Optional[str] = None
    members: List[UUID]
    inserted_at: datetime
    updated_at: datetime


class BotXAPIListChatResponse(APIBaseModel):
    status: Literal["ok"]
    result: List[BotXAPIListChatResult]

    def to_domain(self) -> List[ChatListItem]:
        return [
            ChatListItem(
                chat_id=chat_item.group_chat_id,
                chat_type=convert_chat_type_to_domain(chat_item.chat_type),
                name=chat_item.name,
                description=chat_item.description,
                members=chat_item.members,
                inserted_at=chat_item.inserted_at,
                updated_at=chat_item.updated_at,
            )
            for chat_item in self.result
        ]


class ListChatsMethod(AuthorizedBotXMethod):
    async def execute(self) -> BotXAPIListChatResponse:
        path = "/api/v3/botx/chats/list"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
        )

        return self._extract_api_model(BotXAPIListChatResponse, response)
