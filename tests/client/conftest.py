from typing import AsyncGenerator
from uuid import UUID

import httpx
import pytest
from loguru import logger

from botx import BotAccount
from botx.bot.bot_accounts_storage import BotAccountsStorage


async def log_request(request: httpx.Request) -> None:
    logger.debug(
        "\n"
        f"Endpoint: {request.method} {request.url}\n"
        f"Headers: {request.headers}\n"
        f"Payload: {request.content!r}",
    )


async def log_response(response: httpx.Response) -> None:
    logger.debug(
        f"\nHeaders: {response.headers}\nStatus code: {response.status_code}\n",
    )


@pytest.fixture
async def httpx_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(
        event_hooks={"request": [log_request], "response": [log_response]},
    ) as client:
        yield client


@pytest.fixture
def prepared_bot_accounts_storage(
    bot_id: UUID,
    bot_account: BotAccount,
) -> BotAccountsStorage:
    bot_accounts_storage = BotAccountsStorage([bot_account])
    bot_accounts_storage.set_token(bot_id, "token")

    return bot_accounts_storage
