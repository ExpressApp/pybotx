from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from botx.client.authorized_botx_method import AuthorizedBotXMethod
from botx.models.enums import APIChatTypes, ChatTypes, convert_chat_type_to_domain
from botx.shared_models.api_base import VerifiedPayloadBaseModel

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore  # noqa: WPS440


@dataclass
class ChatListItem:
    """Chat from list.

    Attributes:
        chat_id: Chat id.
        chat_type: Chat Type.
        name: Chat name.
        description: Chat description.
        members: Chat members.
        created_at: Chat creation datetime.
        updated_at: Last chat update datetime.
    """

    chat_id: UUID
    chat_type: ChatTypes
    name: str
    description: Optional[str]
    members: List[UUID]
    created_at: datetime
    updated_at: datetime


class BotXAPIListChatResult(VerifiedPayloadBaseModel):
    group_chat_id: UUID
    chat_type: APIChatTypes
    name: str
    description: Optional[str] = None
    members: List[UUID]
    inserted_at: datetime
    updated_at: datetime


class BotXAPIListChatResponsePayload(VerifiedPayloadBaseModel):
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
                created_at=chat_item.inserted_at,
                updated_at=chat_item.updated_at,
            )
            for chat_item in self.result
        ]


class ListChatsMethod(AuthorizedBotXMethod):
    async def execute(self) -> BotXAPIListChatResponsePayload:
        path = "/api/v3/botx/chats/list"

        response = await self._botx_method_call(
            "GET",
            self._build_url(path),
        )

        return self._verify_and_extract_api_model(
            BotXAPIListChatResponsePayload,
            response,
        )
