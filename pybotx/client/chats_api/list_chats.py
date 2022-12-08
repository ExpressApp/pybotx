from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pybotx.client.authorized_botx_method import AuthorizedBotXMethod
from pybotx.logger import logger
from pybotx.models.api_base import VerifiedPayloadBaseModel
from pybotx.models.chats import ChatListItem
from pybotx.models.enums import APIChatTypes, convert_chat_type_to_domain


class BotXAPIListChatResult(VerifiedPayloadBaseModel):
    group_chat_id: UUID
    chat_type: APIChatTypes
    name: str
    description: Optional[str] = None
    members: List[UUID]
    inserted_at: datetime
    updated_at: datetime
    shared_history: bool


class BotXAPIListChatResponsePayload(VerifiedPayloadBaseModel):
    status: Literal["ok"]
    result: List[Union[BotXAPIListChatResult, Dict[str, Any]]]  # noqa: WPS234

    def to_domain(self) -> List[ChatListItem]:
        chats_list = [
            ChatListItem(
                chat_id=chat_item.group_chat_id,
                chat_type=convert_chat_type_to_domain(chat_item.chat_type),
                name=chat_item.name,
                description=chat_item.description,
                members=chat_item.members,
                created_at=chat_item.inserted_at,
                updated_at=chat_item.updated_at,
                shared_history=chat_item.shared_history,
            )
            for chat_item in self.result
            if isinstance(chat_item, BotXAPIListChatResult)
        ]

        if len(chats_list) != len(self.result):
            logger.warning("One or more unsupported chat types skipped")

        return chats_list


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
