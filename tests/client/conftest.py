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
def host() -> str:
    return "cts.example.com"


@pytest.fixture
def bot_id() -> UUID:
    return UUID("24348246-6791-4ac0-9d86-b948cd6a0e46")


@pytest.fixture
def bot_signature() -> str:
    return "E050AEEA197E0EF0A6E1653E18B7D41C7FDEC0FCFBA44C44FCCD2A88CEABD130"


@pytest.fixture
def bot_account(host: str, bot_id: UUID) -> BotAccount:
    return BotAccount(
        host=host,
        bot_id=bot_id,
        secret_key="bee001",
    )


@pytest.fixture
def prepared_bot_accounts_storage(
    bot_id: UUID,
    bot_account: BotAccount,
) -> BotAccountsStorage:
    bot_accounts_storage = BotAccountsStorage([bot_account])
    bot_accounts_storage.set_token(bot_id, "token")

    return bot_accounts_storage
