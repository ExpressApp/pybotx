from uuid import UUID

import httpx

from pybotx.bot.bot_accounts_storage import BotAccountsStorage
from pybotx.client.bots_api.get_token import (
    BotXAPIGetTokenRequestPayload,
    GetTokenMethod,
)


async def get_token(
    bot_id: UUID,
    httpx_client: httpx.AsyncClient,
    bot_accounts_storage: BotAccountsStorage,
) -> str:  # noqa: DAR101, DAR201
    """Request token for bot.

    Moved to separate file because used in `AuthorizedBotXMethod` and `Bot.get_token`.
    """

    method = GetTokenMethod(
        bot_id,
        httpx_client,
        bot_accounts_storage,
    )

    signature = bot_accounts_storage.build_signature(bot_id)
    payload = BotXAPIGetTokenRequestPayload.from_domain(signature)

    botx_api_token = await method.execute(payload)

    return botx_api_token.to_domain()
