from typing import List, Optional
from uuid import UUID

import httpx

from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.client.chats_api.create_chat import BotXAPICreateChatPayload, CreateChatMethod
from botx.client.chats_api.list_chats import ChatListItem, ListChatsMethod
from botx.client.get_token import get_token
from botx.client.notifications_api.direct_notification import (
    BotXAPIDirectNotificationPayload,
    DirectNotificationMethod,
)
from botx.shared_models.enums import ChatTypes


class BotXAPIClient:
    def __init__(
        self,
        httpx_client: Optional[httpx.AsyncClient],
        bot_accounts_storage: BotAccountsStorage,
    ) -> None:
        self._httpx_client = httpx_client or httpx.AsyncClient()
        self._bot_accounts_storage = bot_accounts_storage

    async def shutdown(self) -> None:
        await self._httpx_client.aclose()

    # - Bots API -
    async def get_token(self, bot_id: UUID) -> str:
        return await get_token(bot_id, self._httpx_client, self._bot_accounts_storage)

    # - Notifications API -
    async def send_direct_notification(
        self,
        bot_id: UUID,
        body: str,
        chat_id: UUID,
    ) -> UUID:
        method = DirectNotificationMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPIDirectNotificationPayload.from_domain(
            body,
            chat_id,
        )
        botx_api_sync_id = await method.execute(payload)

        return botx_api_sync_id.to_domain()

    # - Chats API -
    async def create_chat(
        self,
        bot_id: UUID,
        name: str,
        chat_type: ChatTypes,
        members: List[UUID],
        description: Optional[str] = None,
        shared_history: bool = False,
    ) -> UUID:
        method = CreateChatMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        payload = BotXAPICreateChatPayload.from_domain(
            name,
            chat_type,
            members,
            description,
            shared_history,
        )
        botx_api_chat_id = await method.execute(payload)

        return botx_api_chat_id.to_domain()

    async def list_chats(
        self,
        bot_id: UUID,
    ) -> List[ChatListItem]:
        method = ListChatsMethod(
            bot_id,
            self._httpx_client,
            self._bot_accounts_storage,
        )

        botx_api_list_chat = await method.execute()

        return botx_api_list_chat.to_domain()
