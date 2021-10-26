from uuid import UUID

import pytest

from botx import BotAccount
from botx.bot.bot_accounts_storage import BotAccountsStorage


@pytest.fixture
def prepared_bot_accounts_storage(
    bot_id: UUID,
    bot_account: BotAccount,
) -> BotAccountsStorage:
    bot_accounts_storage = BotAccountsStorage([bot_account])
    bot_accounts_storage.set_token(bot_id, "token")

    return bot_accounts_storage


@pytest.fixture
def user_huid() -> UUID:
    return UUID("f837dff4-d3ad-4b8d-a0a3-5c6ca9c747d1")
