from typing import List, Optional
from uuid import UUID

import httpx

from botx.bot.bot_accounts_storage import BotAccountsStorage
from botx.bot.models.commands.enums import ChatTypes
from botx.client.chats_api.create_chat import BotXAPICreateChatPayload, CreateChatMethod
from botx.client.get_token import get_token


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

    async def get_token(self, bot_id: UUID) -> str:
        return await get_token(bot_id, self._httpx_client, self._bot_accounts_storage)

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
