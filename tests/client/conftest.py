from typing import AsyncGenerator
from uuid import UUID

import httpx
import pytest

from botx import BotAccount
from botx.bot.bot_accounts_storage import BotAccountsStorage


@pytest.fixture
async def httpx_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture
def prepared_bot_accounts_storage(
    bot_id: UUID,
    bot_account: BotAccount,
) -> BotAccountsStorage:
    bot_accounts_storage = BotAccountsStorage([bot_account])
    bot_accounts_storage.set_token(bot_id, "token")

    return bot_accounts_storage
